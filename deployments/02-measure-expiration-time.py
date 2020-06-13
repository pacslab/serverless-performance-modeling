# %% imports
import boto3
import os
import time
import pytz
import random
from datetime import datetime

from pacsltk import deployer
from pacsltk import client

# Load secrets
from dotenv import load_dotenv
from pathlib import Path  # python3 only
env_path = Path('.') / '.secret-env'
load_dotenv(dotenv_path=env_path)

# Processing Imports
import pandas as pd

from tqdm.auto import tqdm
tqdm.pandas()

from pacswg.timer import *
import pacswg

# Function params
CODE_PATH = {
    'python3.6': os.path.join('.', 'faas-modeling-workload'),
}
region_name = 'us-east-1'
# Add role from environment variable
role = os.getenv("ROLE")
zipped_code_path = os.path.join(os.getcwd(), "pacsltk-tmp.zip")

sample_count = 1000
sample_wait_min = 30
sample_wait_max = 2000
test_timeout = 10 * 24 * 60 * 60
checkpoint_timeout = 1 * 60 * 60

# function specific params
runtime = 'python3.6'
func_handler = "index.handler"
memory = 128
func_name = 'faas-workload-' + str(int(random.random() * 1e4))

# %% Deploy functions

# This automatically loads the logged-in aws session info in ~/.aws
aws_client = boto3.client('lambda', region_name=region_name)

def delete_function():
    print("Deleting...")
    deployer.delete_function(func_name=func_name)
    print("Done!")

def fresh_initialization():
    print("Initializing...")
    
    deployer.initialize(new_client=aws_client)
    print("Done!")

    # To ensure same initial state
    delete_function()

    print("Deploying...")
    deployer.deploy_function(func_name=func_name, func_handler=func_handler, memory=memory,
                            role=role, code_path=CODE_PATH[runtime], runtime=runtime)
    print("Waiting...")
    for i in range(1, 6):
        print(i, end=' ', flush=True)
        time.sleep(1)

    print("Done!")

# define worker function
def worker_func():
    cmds = {}
    cmds['sleep'] = 0
    cmds['sleep_till'] = 0
    cmds['stat'] = {"argv": 1}
    cmds['io'] = {"rd": 3, "size": "1M", "cnt": 5}
    cmds['cpu'] = {"n": 10000}

    payload = {}
    payload['cmds'] = cmds

    res = client.make_request(func_name=func_name, client=aws_client, payload=payload)
    return res


def get_now_with_tz():
    return datetime.now().astimezone(pytz.timezone('US/Eastern'))


def print_current_time():
    print("Time:", get_now_with_tz())


def get_sample_wait():
    return random.random() * (sample_wait_max - sample_wait_min) + sample_wait_min


def get_csv_filename():
    now = get_now_with_tz()
    csv_filename = now.strftime('res-02-%Y-%m-%d_%H-%M-%S.csv')
    return csv_filename


def save_data():
    # Save The Results
    df_res = pd.DataFrame(data=sampled_data)
    print(df_res.head(20))
    df_res.to_csv(os.path.join('results', csv_filename), index=False)
    print("CSV File Name:", csv_filename)

# %% Perform Experiment
print("starting experiment...")
print_current_time()
csv_filename = get_csv_filename()
print()

fresh_initialization()

# timer is used to check timeout
timer = TimerClass()
timer.tic()
checkpointTimer = TimerClass()

# send a cold start request
ret = worker_func()
# get instance info
init_instance_id = ret['exist_id']
curr_instance_id = init_instance_id

sampled_data = []

try:
    # until we gather enough samples
    for _ in tqdm(range(sample_count)):
        if timer.toc() > test_timeout:
            raise Exception("Timeout!")
        if checkpointTimer.toc() > checkpoint_timeout:
            save_data()
            checkpointTimer.tic()

        sample_wait_time = get_sample_wait()
        # wait for the random amount of time
        time.sleep(sample_wait_time)
        # make a new request
        ret = worker_func()
        curr_instance_id = ret['exist_id']
        # add the request to samples
        sampled_data.append({
            "elapsed_time": sample_wait_time,
            "is_expired": ret['is_cold'],
            "inst_id": init_instance_id,
        })

        # switch to new instance if old one died
        if ret['is_cold']:
            init_instance_id = curr_instance_id
finally:
    save_data()
    # Clean up in the end
    delete_function()

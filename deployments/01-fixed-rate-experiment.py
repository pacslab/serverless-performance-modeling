# %% imports
import boto3
import os
import time

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

# function specific params
runtime = 'python3.6'
func_handler = "index.handler"
memory = 128
func_name = 'faas-workload'

# %% Deploy the function
print("Initializing...")
# This automatically loads the logged-in aws session info in ~/.aws
aws_client = boto3.client('lambda', region_name=region_name)
deployer.initialize(new_client=aws_client)
print("Done!")

# To ensure same initial state
print("Deleting...")
deployer.delete_function(func_name=func_name)
print("Done!")

print("Deploying...")
deployer.deploy_function(func_name=func_name, func_handler=func_handler, memory=memory,
                         role=role, code_path=CODE_PATH[runtime], runtime=runtime)
print("Waiting...")
for i in range(1, 6):
    print(i, end=' ', flush=True)
    time.sleep(1)

print("Done!")

# %% define worker function
def worker_func():
    cmds = {}
    cmds['sleep'] = 0
    cmds['sleep_till'] = 0
    cmds['stat'] = {"argv": 1}
    cmds['io'] = {"rd": 3, "size": "1M", "cnt": 5}
    cmds['cpu'] = {"n": 10000}
    # Other Options:
    # cmds['net'] = {"server_ip": os.getenv("IPERFSERVER"), "port": 5201}
    # cmds['cpuu'] = {"n": 3}

    payload = {}
    payload['cmds'] = cmds

    res = client.make_request(func_name=func_name, client=aws_client, payload=payload)
    return res

# %% Perform Experiment
# Requests per second
rps = 3
# warm up times (not recorded) in minutes
warmup_mins = 10
# total time for the experiment in minutes
total_time = 4*60

wg = pacswg.WorkloadGenerator(worker_func=worker_func, rps=0, worker_thread_count=100)
wg.start_workers()
timer = TimerClass()
tmptimer = TimerClass()

import pytz
from datetime import datetime
print("Time Started:", datetime.now().astimezone(pytz.timezone('US/Eastern')))

for i in range(1,warmup_mins+1):
    wg.set_rps(rps * i / warmup_mins)
    timer.tic()
    while timer.toc() < 1 * 60:
        wg.fire_wait()

wg.set_rps(rps)
wg.reset_stats()
timer.tic()
while timer.toc() < (total_time * 60):
    wg.fire_wait()

wg.stop_workers()

all_res = wg.get_stats()
print("Total Requests Made:", len(all_res))

# %% Save The Results
df_res = pd.DataFrame(data=all_res)
now = datetime.now()
csv_filename = now.strftime('res-01-%Y-%m-%d_%H-%M-%S.csv')
df_res.to_csv(os.path.join('results', csv_filename))

print("CSV File Name:", csv_filename)
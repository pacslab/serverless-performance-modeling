import os

import numpy as np
import pandas as pd
pd.pandas.set_option('display.max_columns', None)
pd.set_option('mode.chained_assignment', None)


from datetime import datetime
from datetime import timedelta

# Import util functions
from pacsltk.pacs_util import *

def read_csv_file(csv_file):
    return pd.read_csv(csv_file, index_col=0, parse_dates=True).dropna()

def preprocess_df(df):
    epoch_millis_cols_list = ['end_time', 'start_time']
    for epoch_col in epoch_millis_cols_list:
        df[epoch_col] = df[epoch_col] / 1000

    df['client_elapsed_time'] = df['client_elapsed_time'] * 1000

    epoch_cols_list = ['client_start_time', 'client_end_time', 'end_time', 'start_time']
    for epoch_col in epoch_cols_list:
        times = df[epoch_col].apply(lambda x: datetime.fromtimestamp(x))
        times = pd.to_datetime(times.dt.to_pydatetime())
        df[epoch_col + '_dt'] = times
    
    return df


def parse_df(df):
    total_time = df['client_start_time_dt'].max() - df['client_start_time_dt'].min()

    # Number of minutes to ignore in the beginning
    ignore_mins = total_time.total_seconds() / 60 / 4
    # print(f"Ignoring {ignore_mins:4.2f} minutes")
    ss_df = df.loc[df['client_start_time_dt'] > (df['client_start_time_dt'].min() + timedelta(minutes=ignore_mins)), :]

    # Response Time Statistics
    total_invocations = df.shape[0]
    mean_reqs_per_min = total_invocations / (total_time.total_seconds() / 60)
    mean_reqs_per_sec = mean_reqs_per_min / 60
    mean_resp_time_client = ss_df['client_elapsed_time'].mean()
    mean_resp_time_aws = ss_df['aws_duration'].mean()

    # Cold/Warm Start Statistics
    cold_df = ss_df.loc[ss_df['is_cold'] == True, :]
    cold_count = cold_df.shape[0]
    #cold_rt = cold_df['aws_duration'].mean()
    cold_rt = cold_df['client_elapsed_time'].mean()
    warm_df = ss_df.loc[ss_df['is_cold'] == False, :]
    warm_count = warm_df.shape[0]
    #warm_rt = warm_df['aws_duration'].mean()
    warm_rt = warm_df['client_elapsed_time'].mean()
    cold_prob = df['is_cold'].mean()
    ss_cold_prob = ss_df['is_cold'].mean()
    
    list_of_vars = ['df', 'ss_df', 'total_time', 'ignore_mins', 'total_invocations', 'mean_reqs_per_min', 'mean_reqs_per_sec', 'mean_resp_time_client',
                   'mean_resp_time_aws', 'cold_count', 'cold_rt', 'warm_count', 'warm_rt', 'cold_prob', 'ss_cold_prob']
    
    
    return get_local_vars_as_dict(list_of_vars, locals())

def parse_instance_info(df, idle_mins_before_kill):
    u_instances = df['inst_id'].unique()
    all_instance_info = []
    for instance_id in (u_instances):
        sub_df = df[df['inst_id'] == instance_id].copy()
        instance_start = sub_df['client_start_time'].min()
        instance_start_dt = sub_df['client_start_time_dt'].min()
        instance_end = sub_df['client_end_time'].max()
        instance_end_dt = sub_df['client_end_time_dt'].max()
        # extended lifetime after sometime with no request
        instance_end_ext = instance_end + (idle_mins_before_kill * 60)
        instance_end_ext_dt = instance_end_dt + timedelta(minutes=idle_mins_before_kill)
        lifetime_mins = (instance_end - instance_start) / 60
        lifetime_mins_ext = lifetime_mins + idle_mins_before_kill
        
        #running_time_mins = sub_df.loc[:,'elapsed_time'].sum() / 1000 / 60
        running_time_mins = sub_df.loc[:,'client_elapsed_time'].sum() / 1000 / 60
        idle_time_mins = lifetime_mins - running_time_mins
        idle_time_mins_ext = lifetime_mins_ext - running_time_mins
        
        list_of_vars = ['instance_id', 'lifetime_mins', 'lifetime_mins_ext', 'instance_start', 'instance_start_dt',
                       'instance_end', 'instance_end_ext', 'instance_end_dt', 'instance_end_ext_dt', 'running_time_mins',
                       'idle_time_mins', 'idle_time_mins_ext']
        all_instance_info.append(get_local_vars_as_dict(list_of_vars, locals()))
        
    df_inst = pd.DataFrame(data=all_instance_info)
    
    instance_end_times = list(df_inst['instance_end'].values)
    
    # add the is_last column (if a request is the last request container is serving)
    df.loc[:, 'is_last'] = df.apply(lambda x: x['client_end_time'] in instance_end_times, axis=1)
    
    list_of_vars = ['df', 'df_inst', ]
    return get_local_vars_as_dict(list_of_vars, locals())


def parse_counting_info(df, ss_df, df_inst, step_seconds):
    time_idx = pd.date_range(start=ss_df['client_start_time_dt'].min(), end=ss_df['client_start_time_dt'].max(), freq='{}S'.format(step_seconds))
    df_counts = pd.DataFrame(data = {'count': 0}, index=time_idx)

    def func_instance_count(x):
        val = ((df_inst.loc[:,'instance_start_dt'] < x.name) & (df_inst.loc[:,'instance_end_ext_dt'] > x.name)).sum()
        if val is not None:
            return val
        else:
            return 0

    df_counts['instance_count'] = df_counts.apply(func_instance_count, axis=1)


    # Remove last n minutes
    df_counts = df_counts.iloc[:-1*int(60/step_seconds),:]

    # get running containers count
    def func_running_count(x):
        val = df.loc[(df.loc[:,'client_start_time_dt'] < x.name) & (df.loc[:,'client_end_time_dt'] > x.name), 'inst_id'].nunique()
        if val is not None:
            return val
        else:
            return 0

    # get running containers count
    def func_running_warm_count(x):
        val = df.loc[(df.loc[:,'client_start_time_dt'] < x.name) & (df.loc[:,'client_end_time_dt'] > x.name) & (df.loc[:,'is_cold'] == False), 'inst_id'].nunique()
        if val is not None:
            return val
        else:
            return 0


    df_counts['running_count'] = df_counts.apply(func_running_count, axis=1)
    df_counts['running_warm_count'] = df_counts.apply(func_running_warm_count, axis=1)
    df_counts['idle_count'] = df_counts['instance_count'] - df_counts['running_count']
    df_counts['utilization'] = df_counts['running_warm_count'] / df_counts['instance_count']

    # get average numbers
    avg_instance_count = df_counts['instance_count'].mean()
    avg_running = df_counts['running_count'].mean()
    avg_idle = avg_instance_count - avg_running
    avg_util = df_counts['utilization'].mean()
    
    list_of_vars = ['df_counts', 'avg_instance_count', 'avg_running', 'avg_idle', 'avg_util']
    return get_local_vars_as_dict(list_of_vars, locals())



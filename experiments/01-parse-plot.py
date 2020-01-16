#%% Imports
import os

from sls_util import *
from exp_parser import *

import matplotlib.pyplot as plt

# import seaborn as sns
# sns.set()

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


#%% Process an experiment file
csv_filename = 'res-01-2020-01-07_20-47-22.csv'
idle_mins_before_kill = 10
step_seconds = 60

csv_file = os.path.join('results', csv_filename)
df = read_csv_file(csv_file)
df = preprocess_df(df)

parse_results = parse_df(df)
# load results into local variables
locals().update(parse_results)

parse_results = parse_instance_info(df, idle_mins_before_kill)
# load results into local variables
locals().update(parse_results)

parse_results = parse_counting_info(df, ss_df, df_inst, step_seconds)
# load results into local variables
locals().update(parse_results)

print(f"ArrivalRate: {mean_reqs_per_sec:4.4f}")
print(f"ServiceTimeWarm: {warm_rt:4.4f}")
print(f"ServiceTimeCold: {cold_rt:4.4f}")
print(f"IdleMinutesBeforeKill: {idle_mins_before_kill:4.4f}")

#%% Make Plots



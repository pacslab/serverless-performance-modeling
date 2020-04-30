# %% Imports
import os

from pacs_util import *
from pacsltk.pacs_util import *
from pacsltk.exp_parser import *

import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# %% Process an experiment file
# csv_filename = 'res-01-2020-01-09_19-59-16.csv'
csv_filename = 'res-01-2020-04-23_03-51-10.csv'
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
print(ss_cold_prob)

# %% Make Plots
figs_folder = "figs"


def get_fig_path(x): return (os.path.join(figs_folder, "exp" +
                                          x + ".png"), os.path.join(figs_folder, "exp" + x + ".pdf"))


def tmp_fig_save(fig_name):
    paths = get_fig_path(fig_name)
    plt.savefig(paths[0], dpi=300)
    plt.savefig(paths[1])


prepare_matplotlib_cycler()

# %% Plot Response Time Over Time
time_index = (df['client_start_time_dt'] - df['client_start_time_dt'].min())
tmp_df = pd.DataFrame(
    data={'client_elapsed_time': df['client_elapsed_time'], 'time_index': time_index})
tmp_df.set_index('time_index', inplace=True)

plt.figure(figsize=(4, 2))
plt.plot(tmp_df['client_elapsed_time'].resample(
    'T').mean()[1:-1], label='RT (1 min average)')
plt.axhline(mean_resp_time_client, color='r',
            linestyle='-.', label='Total Average')
plt.tight_layout()
set_time_idx_ticks(divide_by=1e9)
plt.xlabel("Time (hh:mm)")
plt.ylabel("Service Time (ms)")
plt.ylim((1500, 3000))
plt.gcf().subplots_adjust(left=0.15, bottom=0.2)
plt.grid(True)

tmp_fig_save("01_sample_response_time")

# %% Instance Count Over Time
time_index = df_counts.apply(
    lambda x: x.name - df['client_start_time_dt'].min(), axis=1)
inst_count_until_now = df_counts.apply(
    lambda x: df_counts.loc[df_counts.index < x.name, 'instance_count'].mean(), axis=1)

plt.figure(figsize=(4, 2))
plt.plot(time_index, df_counts['instance_count'],
         label="Current Instance Count")
plt.plot(time_index, inst_count_until_now, label="Instance Count Average")
plt.axhline(avg_instance_count, color='r',
            linestyle='-.', label='Total Average')
plt.legend()
set_time_idx_ticks(divide_by=1e9)
plt.xlabel("Time (hh:mm)")
plt.ylabel("Warm Instance Count")
plt.tight_layout()
plt.gcf().subplots_adjust(left=0.15, bottom=0.2)
plt.grid(True)

tmp_fig_save("03_inst_count_over_time")

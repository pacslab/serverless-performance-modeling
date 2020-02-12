# %% Imports
import os

from pacs_util import *
from exp_parser import *

from pacsltk import perfmodel

import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# %% Make Plots
figs_folder = "figs"


def get_fig_path(x): return (os.path.join(figs_folder, "exp" +
                                          x + ".png"), os.path.join(figs_folder, "exp" + x + ".pdf"))


def tmp_fig_save(fig_name):
    paths = get_fig_path(fig_name)
    plt.savefig(paths[0], dpi=300)
    plt.savefig(paths[1])


prepare_matplotlib_cycler()

# %% Process All Files
num_of_breakdown = 7
idle_mins_before_kill = 10
step_seconds = 60

similar_csvs = ['res-01-2020-01-06_20-44-57.csv', 'res-01-2020-01-07_20-47-22.csv',
                'res-01-2020-01-08_02-57-35.csv', 'res-01-2020-01-08_21-30-40.csv',
                'res-01-2020-01-09_02-17-42.csv', 'res-01-2020-01-09_19-59-16.csv',
                'res-01-2020-01-10_00-54-02.csv', 'res-01-2020-01-15_23-45-39.csv'
                ]

idx = 0
all_df = None
for csv_filename in similar_csvs:
    print("=================== " + csv_filename +
          f"({idx:02d})" + " ===================")

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

    # Get Cold Start Probability
    df_org = df.copy()
    step = int(df_org.shape[0]/num_of_breakdown)
    ss_cold_probs = []
    for i in range(num_of_breakdown):
        tmp_df = df_org.iloc[i*step:(i+1)*step-1, :]
        tmp_res = parse_df(tmp_df)
        ss_cold_probs.append(tmp_res['ss_cold_prob'])

    ss_cold_probs = np.array(ss_cold_probs)
    ss_cold_prob = np.median(ss_cold_probs)

    # Get Model Parameters
    props, props2 = perfmodel.get_sls_warm_count_dist(
        mean_reqs_per_sec, (warm_rt / 1000), (cold_rt / 1000), idle_mins_before_kill * 60)

    exp_data = {
        'ArrivalRate': mean_reqs_per_sec,
        'ServiceTimeWarm': warm_rt,
        'ServiceTimeCold': cold_rt,
        'IdleMinutesBeforeKill': idle_mins_before_kill,
        'AverageInstanceCount': [avg_instance_count, props['avg_server_count']],
        'AverageUtilization': [avg_util, props['avg_utilization']],
        'ColdStartProbability': [ss_cold_prob, props['cold_prob']],
        'AverageRunningInstances': [avg_running, props['avg_running_count']],
        'AverageIdleInstances': [avg_idle, props['avg_idle_count']],
    }

    res_df = pd.DataFrame(data=exp_data, index=[
                          f'experiment_{idx}', f'model_{idx}']).T

    if all_df is None:
        all_df = res_df
    else:
        all_df = pd.concat([all_df, res_df], axis=1)

    idx += 1


# %% Show the results
all_df

# %% Plotting Model Results


def analyze_sls(row):
    props, _ = perfmodel.get_sls_warm_count_dist(**row)
    return pd.Series(props)


exp_fmt = 'd'

exp_cols = [c for c in all_df.columns if "experiment_" in c]
exp_df = all_df.loc[:, exp_cols].T

# Model Predictions
params = {
    "arrival_rate": np.arange(exp_df.loc[:, 'ArrivalRate'].min() / 2, exp_df.loc[:, 'ArrivalRate'].max() + 1, 0.1),
    "warm_service_time": exp_df.loc[:, 'ServiceTimeWarm'].mean() / 1000,
    "cold_service_time": exp_df.loc[:, 'ServiceTimeCold'].mean() / 1000,
    "idle_time_before_kill": idle_mins_before_kill * 60,
}
df = pd.DataFrame(data=params)
df = pd.concat([df, df.apply(analyze_sls, axis=1)], axis=1)

# %% Cold Start Probability Plot
plt.figure(figsize=(4, 2))
plt.plot(df['arrival_rate'], df['cold_prob'] * 100, label='Model Prediction')
plt.plot(exp_df['ArrivalRate'], exp_df['ColdStartProbability']
         * 100, 'k' + exp_fmt, label='Experiment')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.ylabel("$P_{{cold}}$ (%)")
plt.xlabel('$\lambda$')
plt.gcf().subplots_adjust(left=0.15, bottom=0.2)

tmp_fig_save("04_perf_model_p_cold")

# %% Server Count Plot
plt.figure(figsize=(4, 2))
plt.plot(df['arrival_rate'], df['avg_idle_count'], label="Model Prediction")
plt.plot(exp_df['ArrivalRate'], exp_df['AverageIdleInstances'], 'k' + exp_fmt, label="Experiment")
plt.xlabel('$\lambda$')
plt.ylabel("$C_{{i,w}}$")
plt.tight_layout()
plt.legend()
plt.grid(True)
plt.gcf().subplots_adjust(left=0.15, bottom=0.2)

tmp_fig_save("05_perf_model_idle_count")

# %% Utilization Plot
plt.figure(figsize=(4, 2))
plt.plot(df['arrival_rate'], df['avg_utilization'], label='Model Prediction')
plt.plot(exp_df['ArrivalRate'], exp_df['AverageUtilization'], 'k' + exp_fmt, label="Experiment")
plt.grid(True)
plt.legend()
plt.xlabel('$\lambda$')
plt.ylabel("U")
plt.tight_layout()
plt.gcf().subplots_adjust(left=0.15, bottom=0.2)

tmp_fig_save("06_perf_model_utilization")


# %% Caculate MAPE
mod_cols = [c for c in all_df.columns if "model_" in c]
mod_df = all_df.loc[:, mod_cols].T

print("Calculating The Mean Absolute Percentage Error...\n")
for col_name in ['ColdStartProbability', 'AverageInstanceCount', 'AverageUtilization', 'AverageRunningInstances', 'AverageIdleInstances']:
    mod_vals = mod_df[col_name].values
    exp_vals = exp_df[col_name].values
    print(f"{col_name}: {np.mean(np.abs(mod_vals - exp_vals) / mod_vals * 100):4.2f} %")
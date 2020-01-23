# %% Imports
import os

from pacs_util import *
from pacsltk import perfmodel

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from pacswg.timer import *

from tqdm.auto import tqdm
tqdm.pandas()

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


# %% Perform Tractability Analysis
idle_mins_before_kill = 10

def analyze_sls(row):
    timer = TimerClass()
    timer.tic()
    props, _ = perfmodel.get_sls_warm_count_dist(**row)
    t = timer.toc()
    props['ProcessingTime'] = t
    return pd.Series(props)

params = {
    "arrival_rate": np.arange(1, 1000, 10),
    "warm_service_time": 2.0,
    "cold_service_time": 2.2,
    "idle_time_before_kill": idle_mins_before_kill * 60,
}

df = pd.DataFrame(data=params)
df = pd.concat([df, df.progress_apply(analyze_sls, axis=1)], axis=1)

# %% Plot The Processing Times
plt.figure(figsize=(4, 2))
plt.plot(df['arrival_rate'], df['ProcessingTime'])
plt.xlabel("$\lambda$")
plt.ylabel("Processing Time (s)")
plt.tight_layout()
plt.grid(True)

tmp_fig_save("07_tractability_analysis")

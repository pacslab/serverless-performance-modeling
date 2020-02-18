import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cycler import cycler
from datetime import datetime
from datetime import timedelta


# For parallelizing the pandas apply
from multiprocessing import Pool, cpu_count

# Source of function: https://towardsdatascience.com/make-your-own-super-pandas-using-multiproc-1c04f41944a1


def parallelize_dataframe(df, func, n_cores=cpu_count()):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


def get_local_vars_as_dict(list_of_vars, local_vars):
    ret = {}
    for v in list_of_vars:
        ret[v] = local_vars[v]
    return ret

def set_time_idx_ticks(divide_by=1e9):
    """set_time_idx_ticks fixes the time index ticks in x axis
    
    :param divide_by: what number do we divide the index by to achieve seconds, defaults to 1
    :type divide_by: int, optional
    """    
    plt.gca().set_xticklabels([(datetime(year=2020,month=1,day=1)+timedelta(seconds=(int(x/divide_by)))).strftime('%H:%M') for x in plt.gca().get_xticks()]);

def prepare_matplotlib_cycler():
    SMALL_SIZE = 8
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 12

    font = {'family': 'serif', 'size': BIGGER_SIZE}
    plt.rc('font', **font)

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    plt.rc('axes', prop_cycle=(cycler(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                                             '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                                             '#bcbd22', '#17becf']) +
                               cycler(linestyle=['-', '--', ':', '-.', '-', '-.', ':', '-.', '-', '--'])))

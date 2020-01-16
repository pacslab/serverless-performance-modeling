import numpy as np
import pandas as pd

# For parallelizing the pandas apply
from multiprocessing import  Pool, cpu_count

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




import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta



def set_time_idx_ticks(divide_by=1e9):
    """set_time_idx_ticks fixes the time index ticks in x axis
    
    :param divide_by: what number do we divide the index by to achieve seconds, defaults to 1
    :type divide_by: int, optional
    """    
    plt.gca().set_xticklabels([(datetime(year=2020,month=1,day=1)+timedelta(seconds=(int(x/divide_by)))).strftime('%H:%M') for x in plt.gca().get_xticks()]);


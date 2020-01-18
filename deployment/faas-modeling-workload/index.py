#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import time
import os

from shutil import copyfile
copyfile('./iperf3', '/tmp/iperf3')
os.chmod('/tmp/iperf3', 0o555)


from stats import *
from tests import *


def run_cmd(cmd):
    return os.popen(cmd).read().strip("\n")


def handler(event, context):
    # start timer
    tm_st = time.time() * 1000

    # add the path for the external code
    os.environ['PATH'] = os.environ['PATH'] + \
        ':' + os.environ['LAMBDA_TASK_ROOT']

    # the map for converting parameters to tests
    CMD_2_FUNC = {
        "stat": stat_basic,
        "sleep": 0,
        "sleep_till": 0,
        "run": run_cmd,
        "io": ioload_test,
        "net": network_test,
        "cpu": cpu_test,
        "cpuu": cpu_util_test
    }

    cmds = event["cmds"]

    # sleep until specified time
    wait_util = int(cmds["sleep_till"])
    cmds.pop("sleep_till", None)

    while time.time() * 1000 < wait_util:
        continue

    # sleep for specified time
    wait_util = int(cmds["sleep"]) + (time.time() * 1000)
    cmds.pop("sleep", None)

    while time.time() * 1000 < wait_util:
        continue


    basic_info = {}
    for k in cmds:
        # if false, skip the test
        if not cmds[k]:
            continue
        # find the tests to run based on the parameter
        func = CMD_2_FUNC[k]
        para = cmds[k]
        try:
            res = func(**para)
        except BaseException as e:
            res = None
            print('error: ', e)
            # import traceback
            # traceback.print_exc(file=sys.stdout)
        # collect all results
        # basic_info[k] = str(res)
        basic_info[k] = res

    tm_ed = time.time() * 1000

    # record coldstart time
    timing_info = [fstr(tm_st), fstr(tm_ed), fstr(tm_ed - tm_st)]
    basic_info['start_time'] = tm_st
    basic_info['end_time'] = tm_ed
    basic_info['elapsed_time'] = (tm_ed - tm_st)

    # res = '#'.join(basic_info + timing_info)
    # return res

    return json.dumps(basic_info)


#########################

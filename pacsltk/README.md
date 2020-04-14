# PACSLTK (PACS Lambda ToolKit)

Developed in PACS Lab to ease the process of deployment and testing of our benchmarking workload
to AWS Lambda. To see how you can use pacsltk, check out the [github repository](https://github.com/nimamahmoudi/serverless-performance-modeling).

## Installation

```sh
pip install pacsltk
```

## Examples

You can use the package as simple as the short code snippet below:

```py
from pacsltk import perfmodel

arrival_rate = 100
warm_service_time = 2
cold_service_time = 25
idle_time_before_kill = 10*60

print("arrival_rate:", arrival_rate)
print("warm_service_time:", warm_service_time)
print("cold_service_time:", cold_service_time)
print("idle_time_before_kill:", idle_time_before_kill)

props1, props2 = perfmodel.get_sls_warm_count_dist(arrival_rate, warm_service_time, cold_service_time, idle_time_before_kill)
perfmodel.print_props(props1)
```

which produces an output similar to the following:

```
arrival_rate: 100
warm_service_time: 2
cold_service_time: 25
idle_time_before_kill: 600

Properties:
------------------
avg_server_count: 251.043927
avg_running_count: 200.148828
avg_running_warm_count: 199.987058
avg_idle_count: 51.056869
cold_prob: 0.000065
avg_utilization: 0.796622
avg_resp_time: 2.001488
rejection_prob: 0.000000
rejection_rate: 0.000000
------------------
```

## Updating README in RST file

```sh
pandoc -s README.md -o README.rst
```

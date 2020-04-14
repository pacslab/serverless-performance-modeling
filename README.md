![PyPI](https://img.shields.io/pypi/v/pacsltk.svg)
![PyPI - Status](https://img.shields.io/pypi/status/pacsltk.svg)
![Travis (.com)](https://img.shields.io/travis/com/nimamahmoudi/serverless-performance-modeling.svg)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/pacsltk.svg)
![GitHub](https://img.shields.io/github/license/pacslab/serverless-performance-modeling.svg)

# Performance Modeling of Serverless Computing Platforms

Package, experimentation results, and other artifacts for our serverless computing performance modeling paper. Using the presented performance model, the serverless computing platform provider and their users can optimize their workload and configurations to adapt to each workload being executed on them. The presented model uses analytical model to calculate steady-state system characteristics.

## Benefits

- Works with any service time distribution (general distribution).
- Calculates steady-state characteristics.
- Is tractable while having a high fidelity.

## Artifacts

Here is a list of different artifacts for the proposed model:

- [Python Package on PyPi](https://pypi.org/project/pacsltk/)
- [Datasets collected throughout experimentations](./experiments/results/)
- [Deployment code for collecting data using experimentations](./deployments/)
- [Code for parsing the datasets and generating plots](./experiments/)
- [Interactive online model](https://nima-dev.com/serverless-performance-modeling/)
- [Jupyter notebook docker image containing the pacsltk package](https://hub.docker.com/repository/docker/nimamahmoudi/jupyter-sls-perf) ([docs](./jupyter_docker/))
- [Flask API for online interactive model](https://hub.docker.com/repository/docker/nimamahmoudi/slsperf-api) ([docs](./web/api/))

## Requirements

- Python 3.6+
- PIP

## Installation

```sh
pip install pacsltk
```

## Usage

Check out the [package documentation](./pacsltk/).

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

```output
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

## License

Unless otherwise specified:

MIT (c) 2020 Nima Mahmoudi & Hamzeh Khazaei

## Citation

You can find the paper with details of the proposed model in [PACS lab website](https://pacs.eecs.yorku.ca/publications/). You can use the following bibtex entry:

```bib
Coming soon...
```

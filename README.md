![PyPI](https://img.shields.io/pypi/v/pacsltk.svg)
![PyPI - Status](https://img.shields.io/pypi/status/pacsltk.svg)
![Travis (.com)](https://img.shields.io/travis/com/nimamahmoudi/serverless-performance-modeling.svg)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/pacsltk.svg)
![GitHub](https://img.shields.io/github/license/nimamahmoudi/serverless-performance-modeling.svg)

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

Coming soon...

## License

Unless otherwise specified:

MIT (c) 2020 Nima Mahmoudi & Hamzeh Khazaei

## Citation

You can find the paper with details of the proposed model in [PACS lab website](https://pacs.eecs.yorku.ca/publications/).

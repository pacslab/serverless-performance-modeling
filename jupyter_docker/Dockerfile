FROM jupyter/datascience-notebook:latest

USER root

# Install Pandoc
# Update with latest version every once in a while: https://github.com/jgm/pandoc/releases/
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        wget ca-certificates openssh-client \
    && wget https://github.com/jgm/pandoc/releases/download/2.7.3/pandoc-2.7.3-1-amd64.deb -O pandoc-amd64.deb \
    && dpkg -i pandoc-amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Install extensions and enable spellchecker
RUN pip install jupyter_contrib_nbextensions && \
    jupyter contrib nbextension install --user && \
    # can modify or enable additional extensions here
    jupyter nbextension enable spellchecker/main --user

COPY jupyter_docker/requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

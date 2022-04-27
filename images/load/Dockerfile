# our base image
FROM python:3.8-slim

# This requires an actual requirements.txt to be in same dir as Dockerfile
# Contains all the required dependencies to run our script
COPY requirements.txt /tmp/requirements.txt

# Installs according to our specified list
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# folderdir relative to Dockerfile
COPY scripts/*.py /usr/local/bin/*
# makes sure that it's executable
RUN chmod +x /usr/local/bin/*

# First command to run when starting a container from this image
# ENTRYPOINT [ "/usr/local/bin/nba-game-ids" ]

# default args to include with ENTRYPOINT cmd
# CMD [ "--help" ]

# Ensures our script, which we've put in /usr/local/bin, is on PATH
# so we can call without specifying full path, and use just the script name
ENV PATH="/usr/local/bin:${PATH}"
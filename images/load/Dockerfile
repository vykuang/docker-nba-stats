# our base image
FROM python:3.8-slim

# This requires an actual requirements.txt to be in same dir as Dockerfile
# Contains all the required dependencies to run our script
COPY requirements.txt /tmp/requirements.txt

# Installs according to our specified list
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# folderdir relative to Dockerfile
COPY scripts/create_log.py /usr/local/bin/create-log
COPY scripts/load.py /usr/local/bin/load
# makes sure that it's executable
RUN chmod +x /usr/local/bin/*

# copies the sql folder; when copying multiple files it must end with a /
# otherwise it is considered a file
COPY sql/*.sql /sql/

# First command to run when starting a container from this image
# ENTRYPOINT [ "/usr/local/bin/nba-game-ids" ]

# default args to include with ENTRYPOINT cmd
# CMD [ "--help" ]

# Ensures our script, which we've put in /usr/local/bin, is on PATH
# so we can call without specifying full path, and use just the script name
# ENV PATH="/usr/local/bin:${PATH}"
# a more robust way to prepend our PATH env var
# this implementation looks at $PATH and checks whether it is already set 
# (as it should) or if it's NULL. 
# If NULL, it evaluates to NULL, and our PATH will consist only
# of /usr/local/bin. If not null, then our path is prepended.
ENV PATH="/usr/local/bin${PATH:+:${PATH}}"

# PATH=$PATH:"/usr/local/bin" is also acceptable, but is slightly different
# in that the path added will be searched last;
# above implementation will search the newly added path FIRST. 
# Mechanically, it's the difference between appending and prepending
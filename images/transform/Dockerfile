# our base image
FROM python:3.8-slim

# This requires an actual requirements.txt to be in same dir as Dockerfile
# Contains all the required dependencies to run our script
COPY requirements.txt /tmp/requirements.txt

# Installs according to our specified list
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# folderdir relative to Dockerfile
COPY scripts/get_new_game_ids.py /usr/local/bin/get-new-ids
# makes sure that it's executable
RUN chmod +x /usr/local/bin/get-new-ids

# First command to run when starting a container from this image
# ENTRYPOINT [ "/usr/local/bin/nba-game-ids" ]

# alternatively, add the above dir to PATH, and call within docker run invoke
# 
ENV PATH="/usr/local/bin:${PATH}"
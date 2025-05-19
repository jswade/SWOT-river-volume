#*******************************************************************************
#Dockerfile
#*******************************************************************************

#Purpose:
#This file describes the operating system prerequisites for SWOT-river-volume, and is
#used by the Docker software.
#Author:
#Cedric H. David, Jeffrey Wade, 2025


#*******************************************************************************
#Operating System
#*******************************************************************************
FROM debian:12.7-slim


#*******************************************************************************
#Copy files into Docker image (this ignores the files listed in .dockerignore)
#*******************************************************************************
WORKDIR /home/swot-river-volume/
COPY . .


#*******************************************************************************
#Operating System Requirements
#*******************************************************************************
RUN  apt-get update && \
     apt-get install -y --no-install-recommends $(grep -v -E '(^#|^$)' requirements.apt) && \
     rm -rf /var/lib/apt/lists/*


#*******************************************************************************
#Python requirements
#*******************************************************************************
ENV PATH="/venv/bin:$PATH"
RUN python3 -m venv /venv/ && \
    pip3 install --no-cache-dir -r requirements.pip && \
    pip3 install --no-cache-dir . &&


#*******************************************************************************
#Intended (default) command at execution of image (not used during build)
#*******************************************************************************
CMD  /bin/bash


#*******************************************************************************
#End
#*******************************************************************************

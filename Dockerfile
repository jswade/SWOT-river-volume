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
ADD https://bootstrap.pypa.io/pip/get-pip.py .
RUN python3 get-pip.py --no-cache-dir \
    `grep 'pip==' requirements.pip` \
    `grep 'setuptools==' requirements.pip` \
    `grep 'wheel==' requirements.pip` && \
    rm get-pip.py

RUN pip3 install --no-cache-dir -r requirements.pip


#*******************************************************************************
#Intended (default) command at execution of image (not used during build)
#*******************************************************************************
CMD  /bin/bash


#*******************************************************************************
#End
#*******************************************************************************

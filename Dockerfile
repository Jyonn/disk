FROM ubuntu

RUN \
  apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y python python-dev python3-pip

RUN pip3 install --upgrade pip
RUN pip3 install virtualenv
RUN ls
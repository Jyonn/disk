FROM ubuntu

RUN \
  apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y python python-dev python3-pip git

RUN pip3 install --upgrade pip

WORKDIR /
RUN git clone https://github.com/lqj679ssn/disk.git
WORKDIR /disk
RUN git checkout istio
RUN pip3 install -r requirements.txt
COPY mysql.local.conf /disk/

EXPOSE 8000
CMD python3 manage.py runserver 8000
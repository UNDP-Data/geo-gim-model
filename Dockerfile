FROM nvidia/cuda:10.1-base

RUN apt-get update --fix-missing && \
    apt-get install -y software-properties-common wget bzip2 ca-certificates && \
    apt-get clean

RUN add-apt-repository ppa:ubuntugis/ppa

RUN apt-get install -y gdal-bin

RUN apt-get install python3  python3-pip

# set the default directory in container
WORKDIR /home/root/

COPY envs/*.yml ./envs/

COPY config.yml /home/root/config.yml

COPY requirements.txt /home/root/requirements.txt

ENV CONFIG_FILE /home/root/config.yml

RUN pip3 install -r requirements.txt

COPY . /home/root/

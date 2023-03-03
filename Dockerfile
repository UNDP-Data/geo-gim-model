FROM nvidia/cuda:10.1-base

RUN apt-get update --fix-missing && \
    apt-get install -y software-properties-common wget bzip2 ca-certificates && \
    apt-get clean

RUN add-apt-repository ppa:ubuntugis/ppa

RUN apt-get install -y gdal-bin

RUN apt-get install python3 python3-pip

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install -e git+https://github.com/UNDP-Data/geo-gim-model.git

# set the default directory in container
WORKDIR /home/root/


COPY config.yml /home/root/config.yml

# copy the requirements file to the container
COPY requirements.txt /home/root/requirements.txt

# set the CONFIG_FILE environment variables
ENV CONFIG_FILE /home/root/config.yml

# install the requirements from the requirements file
RUN pip3 install -r requirements.txt

# install gim-cv package from pypi
RUN pip3 install gim-cv

COPY . /home/root/

FROM nvidia/cuda:11.8.0-base-ubuntu22.04


RUN apt-get update --fix-missing && \
    apt-get install -y software-properties-common bzip2 ca-certificates && \
    apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:ubuntugis/ppa

RUN apt-get install -y gdal-bin

RUN apt-get install -y python3 python3-pip python3.10-venv

RUN python3 -m pip install --upgrade pip

#RUN python3 -m pip install "gim_cv @ git+https://github.com/UNDP-Data/geo-gim-model.git"
#
# set the default directory in container
WORKDIR /home/root/

COPY gim_cv /home/root/package/gim_cv

COPY pyproject.toml /home/root/package/pyproject.toml

WORKDIR /home/root/package

RUN echo "$PWD"

RUN python3 -m pip install build

RUN python3 -m build
RUN python3 -m pip install  $(ls -alh dist/*.whl | awk '{print $9}')
#RUN echo "$(ls -alh dist)"

COPY mainfile.py /home/root/mainfile.py

CMD ["python3", "mainfile.py"]
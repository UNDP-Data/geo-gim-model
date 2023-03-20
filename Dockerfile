FROM nvidia/cuda:11.8.0-base-ubuntu22.04

RUN apt-get update --fix-missing && \
    apt-get install -y software-properties-common bzip2 ca-certificates && \
    apt-get clean \
    && rm -rf var/lib/apt/lists/*

RUN add-apt-repository ppa:ubuntugis/ppa

RUN apt-get install -y gdal-bin

RUN apt-get install -y python3 python3-pip python3.10-venv

RUN python3 -m pip install --upgrade pip

# Create a directory for the package withing the container
WORKDIR /home/root/

# Copy the package directory to the container
COPY gim_cv /home/root/package/gim_cv

# Copy the pyproject.toml file to the package directory
COPY pyproject.toml /home/root/package/pyproject.toml

# Set the package directory to build the gim_cv package
WORKDIR /home/root/package

# This specific requirements.txt file is for packages for running the project but are external to the gim_cv package.
COPY requirements.txt /home/root/requirements.txt

# Install the requirements
RUN python3 -m pip install -r /home/root/requirements.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Print the current working directory
# RUN echo "$PWD"

RUN python3 -m pip install build

# Build the wheel file
RUN python3 -m build

# Find the wheel file and install it
RUN python3 -m pip install  $(ls -alh dist/*.whl | awk '{print $9}')

# Set the package directory back to root directory
WORKDIR /home/root/

# Copy the training script to the container
COPY scripts/training_segmentalist.py /home/root/training_segmentalist.py

# run the training scipts with arguments. These listed arguments are just an example / default arguments. You can change them as you wish.
ENTRYPOINT ["python3", "-u", "scripts/training_segmentalist.py", "--datasets", "train_tif", "--target-spatial-res", "0.4", "--attention-gate", "--overlap-tiles"]
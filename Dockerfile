# FROM nvidia/cuda:11.8.0-base-ubuntu22.04
FROM tensorflow/tensorflow:latest-gpu

RUN apt-get update --fix-missing && apt-get install -y software-properties-common

RUN add-apt-repository ppa:ubuntugis/ppa

RUN apt-get install -y gdal-bin

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install build

WORKDIR /opt

RUN pwd

COPY gim_cv gim_cv

COPY pyproject.toml .

COPY requirements.txt .

RUN python3 -m pip --default-timeout=1000 install -r requirements.txt

# Print the current working directory
# RUN echo "$PWD"

# Build the wheel file
RUN python3 -m build

# Find the wheel file and install it
RUN python3 -m pip --default-timeout=1000 install  $(ls -alh dist/*.whl | awk '{print $9}')

RUN pip install nvidia-tensorrt

RUN rm -rf dist

RUN rm -rf gim_cv.egg-info

RUN pip install dask-image

# Set the package directory back to root directory
WORKDIR /home/root/

COPY scripts scripts

# Copy the training script to the container
# COPY scripts/training_segmentalist.py /home/root/training_segmentalist.py

# Copy the prediction script to the container
# COPY scripts/run_inference_segmentalist.py /home/root/run_inference_segmentalist.py

# run the training scipts with arguments. These listed arguments are just an example / default arguments. You can change them as you wish.
#ENTRYPOINT ["python3", "-u", "scripts/training_segmentalist.py", "-tt", "TRAIN/rasters/train_tile_23.tif", "TRAIN/masks/train_mask_23.tif", "TRAIN/rasters/train_tile_24.tif", "TRAIN/masks/train_mask_24.tif", "TRAIN/rasters/train_tile_27.tif", "TRAIN/masks/train_mask_27.tif", "TRAIN/rasters/train_tile_29.tif", "TRAIN/masks/train_mask_29.tif", "--target-spatial-res", "0.5", "--attention-gate", "--overlap-tiles", "-l", "tversky_loss","-ep", "80"]
#ENTRYPOINT ["python3", "-u", "scripts/training_segmentalist.py", "-d", "train_tif_manilla", "--target-spatial-res", "0.4", "-sag", "-ds", "-ecbam", "-dcbam", "--overlap-tiles", "-l", "dice_coeff_loss","-ep", "80", "-lr", "0.001", "-lrp", "70" , "-bs", "4", "-lrf", "0.5", "-fa"]
#ENTRYPOINT ["python3", "-u", "scripts/run_inference_segmentalist.py", "-td", "train_tif_manilla", "-d", "infer_tif_manilla", "-w", "1024"]
ENTRYPOINT ["python3", "-u", "scripts/training_segmentalist.py", "-d", "my_ds", "--target-spatial-res", "0.4", "--attention-gate", "--overlap-tiles", "-l", "tversky_loss","-ep", "4"]
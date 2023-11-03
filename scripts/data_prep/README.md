GIM CV Segmentalist
===================================

These are the tips and tricks to run training and inferences using Segmentalist from GIM CV.

## Before Training
After ensuring the package is installed and is able to run train on Medellin 40cm test data, make sure the TensorFlow has access to GPU. Ensure runtime:nvidia in docker-compose.yml and FROM tensorflow/tensorflow:latest-gpu in Dockerfile. 

```Dockerfile
FROM tensorflow/tensorflow:latest-gpu
```

```Dockerfile
runtime:nvidia
```
The way the GPU is set up at the moment does not allow access and use of GPU within the container after it is build and used once. Make sure you remove container and image (docker ps -a, docker images) after one round of training/inference. Run docker-compose build and up again. This is fast and it uses the latest image you built. Make sure docker-compose version is updated. 

## Training

For training the model in the case of Metro Manilla, I used the dataset uploaded in this folder and the commands below.

```Dockerfile
ENTRYPOINT ["python3", "-u", "scripts/training_segmentalist.py", "-d", "train_tif_manilla", "--target-spatial-res", "0.4", "-sag", "-ds", "-ecbam", "-dcbam", "--overlap-tiles", "-l", "dice_coeff_loss","-ep", "80", "-lr", "0.001", "-lrp", "70" , "-bs", "4", "-lrf", "0.6", "-fa"]
```

## Inference
The data I used for inference is in this folder, four tiles that cover the entire city of Metro Manilla. The checkpoint files of training results are also available in this folder. Ensure that both training dataset used and inference dataset are defined in datasets.py.

  ```Python
ds_train_tif = Dataset(
    tag='train_tif_manilla',
    spatial_resolution=0.4,
    image_paths = [cfg.train_tif_raster_manilla / Path(tif) for tif in sorted(os.listdir(cfg.train_tif_raster_manilla))],
    mask_paths = [cfg.train_tif_mask_manilla / Path(tif) for tif in sorted(os.listdir(cfg.train_tif_mask_manilla))]
)
```
I used the command below to run our inference for Metro Manilla.
```Dockerfile
ENTRYPOINT ["python3", "-u", "scripts/run_inference_segmentalist.py", "-td", "train_tif_manilla", "-d", "infer_tif_manilla", "-w", "1024"]
```

## Data Preparation
In order to produce training tiles, inference tiles, and post-training processed maps, there are gdals codes in folder ./scripts/data_prep.
The training tiles, training masks, inference tiles, checkpoint files (training results), and a report on replicating Manilla results can be found in undpgeohub storage account, as a blob container called gim. 

---
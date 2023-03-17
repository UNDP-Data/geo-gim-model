## Geo GIM Model Package
The GIM Computer Vision Package

To use this package, you need to have docker installed on your computer. You can download docker from [here](https://www.docker.com/products/docker-desktop).

### Setting up the directory structure
The directory structure should be as follows:

Create any directories that are missing exist.

```
.
├── root
|   ├── data
|   |   ├── local
|   |   ├── processed
|   |   ├── volumes ── ebs_inference_storage
|   |   ├── train
|   |   ├── val
|   ├── gim_cv
|   ├── MODELS
|   ├── INFER
|   ├── TRAIN
|   ├── PREDICTIONS
|   ├── tests
|   ├── saved_models
|   ├── README.md
|   ├── .gitignore
|   ├── .gitattributes
|   ├── .dockerignore
|   ├── Dockerfile
|   ├── docker-compose.yml
|   ├── requirements.txt
```

The Sample dataset is the `Medellin_40cm.tif` that is set in the `datasets.py` module of the `gim_cv` package

Ensure that you have both the raw and mask data in the `TRAIN/raster/Medellin_40cm.tif` and `TRAIN/mask/Medellin_ground_truth.tif` respectively. to run it on the sample dataset.
By default this data is identifiable by the `train_tif` tag in the `datasets.py` module.
So using the default settings, you can run the training script as follows:

```
docker exec -it <CONTAINER-ID> python3 training_segmentalist.py -d train_tif --epochs 10 --batch_size 32 --lr 0.001
```
### Setting up the docker container
To build the container, run the following command in the root directory:
```
docker-compose build
```

To start the container in detached mode, run the following command:
```
docker-compose up -d
```

You can also run the container in interactive mode by running the following command:
```
docker-compose up
```
This will allow you to see the container logs in the terminal. The project at this point is running the `training_segmentalist.py` script. You can stop the container by pressing `Ctrl+C`.
### Training the model
To train the Segmentalist model using custom data, run the following command in the root directory:
```
docker exec -it <CONTAINER-ID> python3 training_segmentalist.py -tt /Path/To/First/Raster.tif /Path/To/First/Mask.tif /Path/To/Second/Raster.tif /Path/To/Second/Mask.tif --epochs 10 --batch_size 32 --lr 0.001
```
The `CONTAINER-ID` can be found by running the following command:
```
docker ps
```
The `CONTAINER-ID` is the first column in the output of the above command. The `training_segmentalist.py` script takes in the following arguments:
```
Usage: python3 training_segmentalist.py [-h] [-tt TRAINING_GEOTIFFS [TRAINING_GEOTIFFS ...]] [-d DATASETS]
                             [-tsr TARGET_SPATIAL_RESOLUTION] [-pp | -npp] [-ds | -nds] [-lc | -nlc]
                             [-ecbam | -necbam] [-dcbam | -ndcbam] [-sag | -nsag | -csag | -ncsag]
                             [-lb LAYER_BLOCKS] [-ldb LAST_DECODER_LAYER_BLOCKS] [-if INITIAL_FILTERS]
                             [-rf RESIDUAL_FILTERS] [-ik INITIAL_KERNEL_SIZE] [-hk HEAD_KERNEL_SIZE]
                             [-cd CARDINALITY]

optional arguments:
  -h, --help            show this help message and exit
  -tt TRAINING_GEOTIFFS [TRAINING_GEOTIFFS ...], --training-geotiff TRAINING_GEOTIFFS [TRAINING_GEOTIFFS ...]
                        A list of geotiff files to train on
  -d DATASETS, --datasets DATASETS
                        Comma delimited string of dataset tags. Available datasets are:
                        train_tif
  -tsr TARGET_SPATIAL_RESOLUTION, --target-spatial-res TARGET_SPATIAL_RESOLUTION
                        spatial resolution to resample to. native resolution for all datasets if == 0.
  -pp, --input-pyramid  Enable input pyramid
  -npp, --no-input-pyramid
                        Disable input pyramid
  -ds, --deep-supervision
                        Enable deep supervision
  -nds, --no-deep-supervision
                        Disable deep supervision
  -lc, --lambda-conv    Replace main 3x3 convolutions in residual blocks with Lambda convolutions
  -nlc, --no-lambda-conv
                        Don't replace main 3x3 convolutions in residual blocks with Lambda convolutions
  -ecbam, --encoder-cbam
                        enable CBAM blocks in encoder residual blocks
  -necbam, --no-encoder-cbam
                        disable CBAM blocks in encoder residual blocks
  -dcbam, --decoder-cbam
                        enable CBAM blocks in decoder residual blocks
  -ndcbam, --no-decoder-cbam
                        disable CBAM blocks in decoder residual blocks
  -sag, --attention-gate
                        Enable spatial attention gate
  -nsag, --no-attention-gate
                        Disable spatial attention gate
  -csag, --channel-spatial-attention-gate
                        Enable channel-spatial attention gate
  -ncsag, --no-channel-spatial-attention-gate
                        Disable channel-spatial attention gate
  -lb LAYER_BLOCKS, --layer-blocks LAYER_BLOCKS
                        Comma-delimited list of the number of residual blocks per layer of the encoder. The last number fixes
                        those in the bridge which is unique. The decoder mirrors these blocks excluding the bridge. The final
                        block of the decoder uses the last_layer_decoder_blocks argument to fix the number of residual convblocks.
  -ldb LAST_DECODER_LAYER_BLOCKS, --last-decoder-layer-blocks LAST_DECODER_LAYER_BLOCKS
                        The number of residual conv blocks in the final decoder block.
  -if INITIAL_FILTERS, --initial-filters INITIAL_FILTERS
                        The number of filters in the first large-kernel-size ResNet convolution in the encoder.
  -rf RESIDUAL_FILTERS, --residual-filters RESIDUAL_FILTERS
                        Comma-delimited list of the number of filters in the residual convolutions in the encoder and decoder.
  -ik -initial-kernel-size The kernel size for the initial convolution in the encoder block. Usually ResNet style 7x7.
    -hk -head-kernel-size The kernel size for the head (final segmentation layer). Typically 1x1.
    -cd -cardinality The cardinality of ResNeXt grouped convolutions in main blocks (if lambda_conv is false).
    -act -activation String name of activation function used throughout.
    -dsmp -downsample Mechanism used for downsampling feature maps: "pool" or "strides".
    -s -patch-size No. of pixels per image patch used for training.
    -ot -overlap-tiles Flag to toggle on overlapping tiles in training data (half-step).
    -not -no-overlap-tiles Flag to toggle off overlapping tiles in training data (half-step) (no overlapping).
    -ep -epochs No. of training epochs.
    -bs -batch_size Batch size.
    -l -loss-fn Loss function name as string (looks in building_age.losses). Optionally provide kwargs afterwards using a colon to delineate the beginning of comma-separated keyword args, e.g. `custom_loss_fn:gamma=1.5,alpha=0.2`.
    -opt -optimiser Gradient descent optimizer (adam, sgd or ranger).
    -swa -stochastic-weight-averaging Apply stochastic weight averaging to optimizer.
    -nswa -no-stochastic-weight-averaging Do not apply stochastic weight averaging to optimizer.
    -dswa -duration-swa No. of epochs before last where SWA is applied.
    -pswa -period-swa Period in epochs over which to average weights with SWA.
    -vl -use-val Switch: evaluate on validation data every epoch and track this.
    -p -patience Patience.
    -rs -seed Random seed.
    -vf -val-frac Validation fraction.
    -tf -test-frac Test fraction.
    -fa -fancy-augs Flag whether to use fancy augmentations (albumentations + FancyPCA).
    -lr -lr-init Initial learning rate.
    -lrmin -lr-min Minimum learning rate if reduce LR on plateau callback used.
    -lrf -lr-reduce-factor Multiplicative LR reduction factor for reduce LR on plateau callback.
    -lrp -lr-reduce-patience Epochs patience for LR reduction application if reduce LR on plateau.
    -ocp -use-ocp Enable one-cycle policy (not used atm).
    -ba -balanced-oversample Oversample training arrays to balance different datasets. Makes an "epoch" much longer.
    -md -model-dir Directory to save model checkpoints to.
    -dt -dump-test-data Dump test arrays to zarr.
    -da -dump-first-batches Precalculate first chunk of training array and dump to disk for inspection.
    -c -use-cache Try to read preprocessed arrays from file if serialised.
    -sc -save-to-cache Save preprocessed arrays to file for future training runs.
 ```
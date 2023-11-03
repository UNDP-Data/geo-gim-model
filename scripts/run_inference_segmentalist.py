"""
run_inference.py

Runs inference with a Segmentalist segmentation model on a particular dataset.

The segmentation model is selected by providing the training datasets
it should have been trained on as arguments. The script will then search
the saved models directory for a model trained on these datasets, and select
the one with the lowest validation loss to run the inference.

The datasets on which inference should be run are specified by their string 
tags and should correspond to datasets defined in gim_cv/datasets.py. If you 
want to add a new dataset, define one in datasets.py and assign it a tag, then 
it should be visible to this script.

The resulting segmentation masks will be output in the directory where the first
source raster is found, under a new subdirectory `seg_outputs`.
"""
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import argparse
import numpy as np
import tensorflow as tf
import gim_cv.config as cfg
import gim_cv.datasets as datasets
from gim_cv.models.segmentalist import Segmentalist

sys.path.append(str(Path(__file__).parent.parent / Path('bin')))

from bin.utils import collate_run_data

# select model directory (containing directories output by training script) ** check config file **
models_dir = cfg.models_path  # / Path('MODELS')# /

# define and parse command-line arguments to script
parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument(
    '-d', '--datasets', dest='datasets', type=str,
    default='predict_tif',  # default='lux_18_rgb,lux_19_rgb,lux_19_true_20cm',
    help='(Comma-delimited) dataset(s) on which to run inference.'
)
parser.add_argument(
    '-td', '--training-datasets', dest='training_datasets', type=str,
    default='train_tif',  # default='lux_belair_all_20cm,potsdam',
    help=('(Comma-delimited) dataset(s) used to select trained model '
          '(i.e. the datasets on which the desired model should have been trained)')
)
parser.add_argument(
    '-w', '--window-size', dest='window_size', type=int, default=1024,
    help='The integer pixel size (of each side) of the square patch used for inference'
)
parser.add_argument(
    '-r', '--spatial-resolution', dest='target_spatial_resolution', type=float, default=0.,
    help=('The resolution to resample the target dataset(s) to (if any - the default 0. '
          'implies no resampling <=> native resolution)')
)
parser.add_argument('-o', '--output-dir', dest='output_dir', type=str, default=str(cfg.predictions_data_tif_path),
                    help=('Output directory for segmentation results. Defaults to '
                          'the parent directory of the input rasters / seg_outputs.')
                    )
parser.add_argument(
    '-l', '--loss-fn', dest='loss_fn', type=str, default='dice_coeff_loss',
    help='Loss function used to train model.'
)
args = parser.parse_args()

log = logging.getLogger(__name__)

# assert tf.test.is_gpu_available(), "GPU not available?"


if __name__ == "__main__":

    # function to convert a string representation of a list to a list of integers - wrong readings were made from checkpoints tf
    def str_to_list(s):
        return [int(x) for x in s.strip('[]').split(',')]

    ds_tags = args.datasets.split(',')
    # find and load the lowest loss model
    df_trained_models = collate_run_data(models_dir, model_name="Segmentalist")

    print(len(df_trained_models))
    
    # any particular selection from the pool of results 
    # print(df_trained_models['optimiser'].unique())
    # df_trained_models.dropna(subset=['lowest_val_loss'],inplace=True)
    # df_sorted = df_trained_models.sort_values(by='lowest_val_loss').query(
    #     f'datasets == "{args.training_datasets}" and loss_fn == "{args.loss_fn}"'
    # )

    df_sorted = df_trained_models.sort_values(by='lowest_val_loss').query(f'loss_fn == "{args.loss_fn}"')
    # check GPU 
    if tf.test.is_gpu_available():
        print("GPU available.")
        print(tf.config.list_physical_devices('GPU'))
    else:
        print("GPU not available.")
    
    gpus = tf.config.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(gpus[0], True)
    
    # apply the conversion function to each cell in the dataframe
    df_sorted["residual_filters"] = df_sorted["residual_filters"].apply(str_to_list)
    df_sorted["layer_blocks"] = df_sorted["layer_blocks"].apply(str_to_list)
    print(df_sorted.columns)
    best_row = df_sorted.iloc[0]
    
    # Selecting a specific training result as below
    #best_row = df_sorted.loc[df_sorted['uuid4']=='72f093fa-4001-40b0-bbd1-6da44811f018']
    #best_row = best_row.iloc[0]
    
    log.info("loading model...")
    log.info(best_row)
    model = Segmentalist.load_from_metadata(best_row, opt = best_row.optimiser)
    # TODO LM: fix load_from_metadata so these lines not needed
    model(np.random.rand(1, args.window_size, args.window_size, 3) ,training = False)
    model.load_weights(best_row.lowest_val_loss_ckpt)
    log.info("model loaded.")

    # run inference for each requested dataset sequentially
    for ds_tag in ds_tags:
        inference_window_size = args.window_size  # implicit here, will need to feed explicitly again to model

        # create inference dataset
        ds = datasets.get_dataset(ds_tag)
        target_spatial_resolution = (
            ds.spatial_resolution if not args.target_spatial_resolution else args.target_spatial_resolution)
        ids = ds.load_inference_data(
            resample_factor=ds.spatial_resolution / target_spatial_resolution,
            inference_window_size=inference_window_size
        )
        ids.prepare()
        # save
        if not args.output_dir:
            output_path = Path(
                cfg.predictions_data_tif_path)  # ds.image_paths[0].parent / Path(f'seg_outputs/{args.loss_fn}/')
        else:
            output_path = Path(args.output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        # prepare inference with model
        ids.schedule_inference(
            model,
            output_directory=output_path
        )
        log.info("inference job scheduled")

        # run inference
        try:
            log.info("generating mask rasters...")
            ids.write_mask_rasters(overwrite=False)
        # anticipate keras stop_training bug
        except:
            print(f"something went wrong with dataset: {ds} raster: {ids.currently_writing_ds.mask_writer.raster_path}")
            raise

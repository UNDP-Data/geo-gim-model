from osgeo import gdal
from osgeo import ogr, osr

import os
import subprocess


def get_image_dimensions(input_tiff):
    """
    Get the width and height of an input georeferenced TIFF image.

    Args:
        input_tiff (str): Path to the input georeferenced TIFF image.

    Returns:
        tuple: Width and height of the image as (width, height).
    """
    ds = gdal.Open(input_tiff, gdal.GA_ReadOnly)

    if ds is None:
        raise ValueError(f"Unable to open the TIFF file: {input_tiff}")

    width = ds.RasterXSize
    height = ds.RasterYSize

    ds = None

    return width, height

def split_tiff(input_tiff, output_dir, n):
    """
    Split a rectangular TIFF image into n equal-sized tiles.

    Args:
        input_tiff (str): Path to the input TIFF image.
        output_dir (str): Directory where the output tiles will be saved.
        n (int): Number of tiles to produce (even number).

    Returns:
        list: List of paths to the output tiles.
    """

    os.makedirs(output_dir, exist_ok=True)

    width, height = get_image_dimensions(input_tiff)

    tile_width = width // (n // 2)
    tile_height = height // (n // 2)

    remaining_width = width % (n // 2)
    remaining_height = height % (n // 2)

    output_tiles = []

    for i in range(n // 2):
        for j in range(n // 2):
            output_tile = os.path.join(output_dir, f"man_tile_{i}_{j}.tif")
            x_offset = i * tile_width
            y_offset = j * tile_height

            if i == (n // 2) - 1:
                tile_width += remaining_width
            if j == (n // 2) - 1:
                tile_height += remaining_height

            cmd = [
                'gdal_translate',
                '-srcwin', str(x_offset), str(y_offset), str(tile_width), str(tile_height),
                '-of', 'GTiff',
                '-co', 'COMPRESS=LZW',
                '-co', 'TILED=YES',
                input_tiff,
                output_tile
            ]

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output_tiles.append(output_tile)

    return output_tiles

def merge_georeferenced_tiffs(input_tiffs, output_tiff):
    """
    Merge multiple georeferenced TIFF files into a single raster with the same projection.

    Args:
        input_tiffs (list): List of paths to input georeferenced TIFF files.
        output_tiff (str): Path to the output merged georeferenced TIFF file.

    Returns:
        None
    """

    first_ds = gdal.Open(input_tiffs[0], gdal.GA_ReadOnly)
    projection = first_ds.GetProjection()
    geotransform = first_ds.GetGeoTransform()

    # Determine the common extent (bounding box) of all input TIFFs
    min_x, max_x, min_y, max_y = geotransform[0], geotransform[0] + geotransform[1] * first_ds.RasterXSize, geotransform[3] + geotransform[5] * first_ds.RasterYSize, geotransform[3]
    
    for input_path in input_tiffs:
        ds = gdal.Open(input_path, gdal.GA_ReadOnly)
        geo = ds.GetGeoTransform()

        min_x = min(min_x, geo[0])
        max_x = max(max_x, geo[0] + geo[1] * ds.RasterXSize)
        min_y = min(min_y, geo[3] + geo[5] * ds.RasterYSize)
        max_y = max(max_y, geo[3])

    width = int((max_x - min_x) / geotransform[1])
    height = int((max_y - min_y) / abs(geotransform[5]))

    driver = gdal.GetDriverByName("GTiff")
    output_ds = driver.Create(output_tiff, width, height, 1, gdal.GDT_Float32)

    output_ds.SetProjection(projection)
    output_ds.SetGeoTransform((min_x, geotransform[1], 0, max_y, 0, geotransform[5]))

    for input_path in input_tiffs:
        input_ds = gdal.Open(input_path, gdal.GA_ReadOnly)
        data = input_ds.GetRasterBand(1).ReadAsArray()
        x_offset = int((input_ds.GetGeoTransform()[0] - min_x) / geotransform[1])
        y_offset = int((max_y - input_ds.GetGeoTransform()[3]) / abs(geotransform[5]))
        output_ds.GetRasterBand(1).WriteArray(data, xoff=x_offset, yoff=y_offset)

    output_ds = None
    first_ds = None



input_tiff = "/Users/zahra/Documents/UNDP_Intern/Data/Manilla/Manilla_rgb_raster_geotif.tif"
output_dir = '/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra'
n = 4

# tiles = split_tiff(input_tiff, output_dir, n)
# print("Output tiles:", tiles)

dir_path = '/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/infer/Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018/'
input_tiffs = []
for file in os.listdir(dir_path):
    # check only text files
    if file.endswith('.tif'):
        input_tiffs.append(dir_path+file)
print(input_tiffs)
output_tiff = '/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/infer/Manilla_Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018.tif'

merge_georeferenced_tiffs(input_tiffs, output_tiff)
print(f"Merged TIFF saved to {output_tiff}")

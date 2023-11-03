from osgeo import gdal
from osgeo import ogr, osr
import os
import subprocess
# import sys
# import argparse

def GetExtent(ds):
    """ Return list of corner coordinates from a gdal Dataset """
    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel

    return (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)

def TransformPix(xpix_1, ypix_1, geo_transform):
    """ Return geocoordinate of pixle """
    georef_x = geo_transform[0] + xpix_1 * geo_transform[1] + ypix_1 * geo_transform[2]
    georef_y = geo_transform[3] + xpix_1 * geo_transform[4] + ypix_1 * geo_transform[5]
    return((georef_x, georef_y))

def CenterTile(x,y,dimx,dimy,resx,resy):
    """ Returns center of a tile """

    width = dimx * resx
    height = dimy * resy
    center_x = x + (width / 2)
    center_y = y + (height / 2)
    return center_x, center_y

def crop_tile(n, in_path, out_path, window_dims=(2560,2560), seed=42):
    """ Creates n random square windows from raster image """

    mask_layer = ogr.Open(in_path_mask, 1)
    raster_layer = gdal.Open(in_path)
    geo_transform = raster_layer.GetGeoTransform()

    sample_locs = []
    sample_georefs = []
    
    for _ in range(n):
        x = random.randint(0, raster_layer.RasterXSize - window_dims[0])
        y = random.randint(0, raster_layer.RasterYSize - window_dims[1])
        sample_locs.append((x, y))
        georef_corner = TransformPix(x,y,geo_transform)
        sample_georefs.append(georef_corner)

    for sample_index, (x, y) in enumerate(sample_locs):
        # mask windows from taining mask shapefile
        sample_mask = []
        output_mask = f"{out_path}/train_shp/train_mask_{sample_index}.shp"
        last_corner = TransformPix(x+window_dims[0], y+window_dims[1], geo_transform)
        x_c,y_c = CenterTile(sample_georefs[sample_index][0],sample_georefs[sample_index][1],window_dims[0], window_dims[1],geo_transform[1], abs(geo_transform[5]))
        subprocess.call(["ogr2ogr", "-f", "ESRI Shapefile", str(output_mask), str(in_path_mask), "-nlt", "POLYGON", "-skipfailures", "-s_srs", "EPSG:32651", "-t_srs", "EPSG:32651", "-clipsrc", str(sample_georefs[sample_index][0]), str(sample_georefs[sample_index][1]), str(last_corner[0]), str(last_corner[1]), "-clipsrcwhere", f"NOT INTERSECTS(geometry, ST_Buffer(ST_Envelope(GeometryFromText('POINT({x_c} {y_c})', 32651)), 0.25))"])
        
        # rgb windows from taining rgb input tifs
        sample_data = []
        for band_index in range(raster_layer.RasterCount):
            band = raster_layer.GetRasterBand(band_index + 1)
            band_data = band.ReadAsArray(x, y, window_dims[0], window_dims[1])
            sample_data.append(band_data)
    
        output_file = f"{out_path}/train_tile/train_tile_{sample_index}.tif"
        driver = gdal.GetDriverByName("GTiff")
        output_raster = driver.Create(output_file, window_dims[0], window_dims[1], raster_layer.RasterCount, band.DataType)
        for band_index in range(raster_layer.RasterCount):
            output_raster.GetRasterBand(band_index + 1).WriteArray(sample_data[band_index])
        
        new_geo_transform = (sample_georefs[sample_index][0],geo_transform[1],geo_transform[2],sample_georefs[sample_index][1],geo_transform[4], geo_transform[5])
        output_raster.SetGeoTransform(new_geo_transform)
        output_raster.SetProjection(raster_layer.GetProjection()) 
        output_raster = None
    
    raster_layer = None

def get_tile_list(n):
    ''' Returns a list of shapefile tiles'''

    layers = []
    refs = []
    for i in range(n):
        layers.append(f"{out_path}/train_shp/train_mask_{i}.shp")
        refs.append(f"{out_path}/train_tile/train_tile_{i}.tif")
    return layers, refs

def to_mask(layers, ref_raster, out_path):
    """ Creates mask layers from shapefile polygons """

    for i in range(len(layers)):
        
        raster_ds = gdal.Open(ref_raster[i])
        geotransform = raster_ds.GetGeoTransform()
        pixel_size_x = geotransform[1]  # Pixel size in X direction
        pixel_size_y = abs(geotransform[5])  # Pixel size in Y direction
        ref_proj = raster_ds.GetProjection()
        pxx = raster_ds.RasterXSize
        pxy = raster_ds.RasterYSize
        raster_ds = None
        driver = gdal.GetDriverByName('GTiff')
        file_name = layers[i]
        base_name = file_name[:file_name.rfind('.')]
        last_three_characters = ''
        last_three_characters = base_name[-4:]
        output_file = f"{out_path}/train_mask/train_mask_{last_three_characters}.tif"
        output_raster = driver.Create(output_file, pxx, pxy, 1, gdal.GDT_Byte)
        output_raster.SetGeoTransform(geotransform)
        output_raster.SetProjection(ref_proj)
        shapefile = ogr.Open(layers[i])
        layer = shapefile.GetLayer()
        extent = layer.GetExtent()
        gdal.RasterizeLayer(output_raster, [1], layer, burn_values=[1])
        output_raster.FlushCache()
        output_raster = None
        shapefile = None


def tiles_in_extents():

    manilla_path = "/Users/zahra/Documents/UNDP_Intern/Data/Manilla"
    in_path_mask = "/Users/zahra/Documents/UNDP_Intern/Data/AI_Shp_Results_HCM_Manila/man_ortho_rgb8_model_ca75fbd0_bin_thres075.shp"

    for i in range(5,10):
        path_i = f"{manilla_path}/train_extents/Manilla_Train_Tile_{i+1}.tif"
        path_o = f"{manilla_path}/from_extent_{i}"
        path_o_1 = f"{path_o}/train_shp"
        path_o_2 = f"{path_o}/train_tile"
        isExist = os.path.exists(path_o)
        if not isExist:
            os.makedirs(path_o)
        
        isExist = os.path.exists(path_o_1)
        if not isExist:
            os.makedirs(path_o_1)
        
        isExist = os.path.exists(path_o_2)
        if not isExist:
            os.makedirs(path_o_2)
        
        crop_tile(10,path_i, path_o)

#in_path = "/Users/zahra/Documents/UNDP_Intern/Data/Manilla/Manilla_rgb_raster_geotif.tif"
#out_path = "/Users/zahra/Documents/UNDP_Intern/Data/Manilla"
manilla_path = "/Users/zahra/Documents/UNDP_Intern/Data/Manilla"
in_path_mask = "/Users/zahra/Documents/UNDP_Intern/Data/AI_Shp_Results_HCM_Manila/man_ortho_rgb8_model_ca75fbd0_bin_thres075.shp"
dir_path = "/Users/zahra/Documents/UNDP_Intern/Data/Manilla/from_all_extents/"

tile_layers, shape_layers = [], []
for file in os.listdir(dir_path):
    # check only text files
    if file.endswith('.shp'):
        shape_layers.append(dir_path+file)
    if file.endswith('.tif'):
        tile_layers.append(dir_path+file)

# print( sorted(os.listdir("/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/11_Tiles/mask/")) )
# print( sorted(os.listdir("/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/11_Tiles/raster/")) )

# shape_layers.sort()
# tile_layers.sort()

# file_name = tile_layers[0]
# base_name = file_name[:file_name.rfind('.')]
# if len(base_name) >= 3:
#     last_three_characters = base_name[-3:]
#     print(last_three_characters)

# print(shape_layers)
# print("********************")
# print(tile_layers)
# to_mask(shape_layers, tile_layers, dir_path)

# x = dir_path + "train_shp_6_6.shp"
# y = dir_path + "train_tile_6_6.tif"
# to_mask([x],[y], dir_path)

# crop_tile(30,in_path_, out_path)
# layers, refs = get_tile_list(70)
# layers = []
# refs = []
# for i in [0,1,3,5,6,7,9,10,11]:
#     layers.append(f"{out_path}/train_shp/train_mask_{i}.shp")
#     refs.append(f"{out_path}/train_tile/train_tile_{i}.tif")
# to_mask(layers, refs, out_path)
import cv2
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal
from osgeo import ogr, osr
import os 

def thresholding_(input_tiffs):
    """
    Threshold pixels of a TIFF image.

    Args:
        input_tiffs (str): Path to the input TIFF images.

    Returns:
        list: List of paths to the output.
    """
    images = []
    for input_tiff in input_tiffs:
        img = cv2.imread(input_tiff, cv2.IMREAD_UNCHANGED)
        images.append(img)
    
    max_height = max(image.shape[0] for image in images)
    images_resized = [cv2.resize(image, (image.shape[1], max_height)) for image in images]
    
    combined_img = np.concatenate(images_resized, axis=1)
    combined_img = combined_img.astype(np.uint8)
    global_threshold_value, otsu_thresholding_global = cv2.threshold(combined_img, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print(global_threshold_value)

    otsu_all = []
    for input_tiff in input_tiffs:
        img = cv2.imread(input_tiff, cv2.IMREAD_UNCHANGED)
        data_type = img.dtype

        # new_max = 100.0
        # new_min = 0.0
        # old_max = img.max()
        # old_min = img.min()
        #scaled_img = ((new_max - new_min) / (old_max - old_min)) * (img - old_min) + new_min
        
        scaled_img = img
        scaled_img = scaled_img.astype(np.uint8)

        t, otsu_thresholding = cv2.threshold(scaled_img,global_threshold_value ,1,cv2.THRESH_BINARY)
        print(t)
        otsu_all.append(otsu_thresholding)
    
    return otsu_all

def georef_(input_tiff, input_png, output_tif):
    
    """
    Georeference PNG.

    Args:
        input_tiff (str): Path to the input TIFF images.
        output_tif (str): Directory where the outputs will be saved.

    Returns:
        list: List of paths to the output.
    """
    for i in range(len(input_png)):
        image = input_png[i]
        src_geotiff = gdal.Open(input_tiff[i])
        driver = gdal.GetDriverByName('GTiff')
        output_ds = driver.Create(output_tif[i], image.shape[1], image.shape[0], 1, gdal.GDT_Byte)

        output_band = output_ds.GetRasterBand(1)
        output_band.WriteArray(image)

        output_ds.SetGeoTransform(src_geotiff.GetGeoTransform())
        output_ds.SetProjection(src_geotiff.GetProjection())

        output_ds = None
        src_geotiff = None

def raster_to_polygon(input_raster, output_vector):
    ds = gdal.Open(input_raster)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(output_vector):
        driver.DeleteDataSource(output_vector)
    out_ds = driver.CreateDataSource(output_vector)
    out_layer = out_ds.CreateLayer('polygons', srs=ds.GetSpatialRef())

    field_defn = ogr.FieldDefn("ID", ogr.OFTInteger)
    out_layer.CreateField(field_defn)

    gdal.Polygonize(ds.GetRasterBand(1), None, out_layer, 0, [])

    ds = None
    out_ds = None  # Close the output data source

if __name__ == '__main__':
    
    dir_path = '/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/infer/Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018/'
    
    input_tiffs = []
    output_tiffs = []
    vectors = []
    for file in os.listdir(dir_path):
        if file.endswith('.tif'):
            input_tiffs.append(dir_path+file)
            # output_tiffs.append(dir_path+'OTSU'+file)
            base_name = file[:file.rfind('.')]
            vectors.append(dir_path+base_name+'.shp')

    for i in range(len(input_tiffs)):
        raster_to_polygon(input_tiffs[i], vectors[i])
    # # input_tiffs = '/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/infer/Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018/Manilla_Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018.tif'
    # output_tif = '/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/infer/Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018/Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018_OTSU.tif'
    # # output_vector = '/Users/zahra/Documents/UNDP_Intern/geo-gim-model/zahra/infer/Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018/Man_Segmentalist_72f093fa-4001-40b0-bbd1-6da44811f018.shp'

    # ds = thresholding_(input_tiffs)
    # georef_(input_tiffs, ds, output_tiffs)

    # for i in range(len(input_tiffs)):
    #     raster_to_polygon(input_tiffs[i], output_vectors[i])

    # raster_to_polygon(output_tif, output_vector)

        # # Convert the thresholded image to the uint8 data type
    # otsu_thresholding = otsu_thresholding.astype(np.float32)
    # # Display the thresholded image
    # plt.figure(figsize=(7, 7))
    # plt.imshow(otsu_thresholding)
    # plt.axis('off')  # Optionally, turn off axis labels
    # plt.show()
    ## plt.imshow(scaled_img)
    # plt.show()

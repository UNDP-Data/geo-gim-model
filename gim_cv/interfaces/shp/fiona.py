import fiona

from gim_cv.interfaces.base import BaseShapeInterface

import logging

from gim_cv.interfaces.shp.ogr import rasterise_shapefile

logger = logging.getLogger(__name__)

class BinaryMaskShapeReader(BaseShapeInterface):
    """ concrete implementation of MaskReader that associates binary masks with shapefiles
        provided a given geo transform/projection/extent
    """
    def read_array_from_shapefile(self):
        """ read with GDAL and burn features onto binary raster mask """
        try:
            logger.debug(f"Reading array from file {self.shp_path}...")
            with fiona.open(self.shp_file, "r") as shapefile:
                shapes = [feature["geometry"] for feature in shapefile]
            self.arr = rasterise_shapefile(layer=self.layer,
                                           projection=self.projection,
                                           geo_transform=self.geo_transform,
                                           raster_x_size=self.raster_x_size,
                                           raster_y_size=self.raster_y_size)
            return self.arr
        except:
            logger.debug("Failed to rasterise shapefile!")
            raise
        finally:
            self.close_shapefile()

#
#t0 = pc()
#
#with rasterio.open(im) as src:
#    out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
#    out_meta = src.meta
#log.debug(f"took {pc() - t0:.2f}s")

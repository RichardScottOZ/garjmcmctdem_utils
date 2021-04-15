'''
Created on 14/6/2020
@author: Neil Symington
This script is for converting aseg-gdf EM data to a netcdf file. The netcdf file will also include some additional
AEM system metadata.
'''

from geophys_utils.netcdf_converter import aseg_gdf2netcdf_converter
import netCDF4
import os, math
import numpy as np
# SO we can see the logging. This enables us to debug
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.debug("test")

# Define paths

def depth_to_thickness(depth):
    """
    Function for calculating thickness from depth array
    :param depth: an array of depths
    :return:
    a flat array of thicknesses with the last entry being a null
    """
    # Create a new thickness array
    thickness = np.nan*np.ones(shape=depth.shape,
                               dtype=np.float)
    # Iterate through the depth array
    if len(depth.shape) == 1:
        thickness[0:-1] = depth[1:] - depth[:-1]
        return thickness

    elif len(depth.shape) == 2:
        thickness[:, 0:-1] = depth[:, 1:] - depth[:, :-1]
        return thickness

    elif len(depth.shape) == 3:

        thickness[:-1,:,:] = depth[1:,:, :] - depth[:-1,:, :]
        return thickness

root = "/home/nsymington/Documents/GA/AEM/GALEIALLATONCE/run1/output"

nc_out_path = os.path.join(root, "Mugrave_galeiallatonce.nc")

dat_in_path = os.path.join(root, 'galeiallatonce.dat')

dfn_in_path = os.path.join(root, 'galeiallatonce.dfn')

# GDA94 MGA zone 52
crs_string = "epsg:28352"

# Initialise instance of ASEG2GDF netcdf converter

settings_file = "/home/nsymington/PycharmProjects/garjmcmctdem_utils/utils/conversion/aseg_gdf_settings.yml"

d2n = aseg_gdf2netcdf_converter.ASEGGDF2NetCDFConverter(nc_out_path,
                                                 dat_in_path,
                                                 dfn_in_path,
                                                 crs_string,
                                                 fix_precision=True,
                                                 settings_path = settings_file)
d2n.convert2netcdf()

# Here we do some processing to ensure our lci file is somewhat standard

# Create a python object with the lci dataset
d = netCDF4.Dataset(nc_out_path, "a")

layer_top_depth = np.zeros(shape = d['thickness'].shape, dtype = np.float32)

layer_top_depth = depth_to_thickness(d['thickness'][:])

layer_top_depth[:] = np.tile(layer_top_depth, d['thickness'].shape[0]).reshape(d['thickness'].shape)

ltop = d.createVariable("layer_top_depth","f8",("point","layer"))
ltop[:] = layer_top_depth

ltop.long_name = "Depth to the top of the layer"
ltop.unit = "m"
ltop.aseg_gdf_format = "30E9.3"

d.close()
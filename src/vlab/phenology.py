#!/usr/bin/env python
import os, sys
import json
#import qm
import rasterio
import rasterio.plot

import datetime
import zipfile
import xarray as xr
import pandas as pd
import rioxarray
import numpy as np
import pyproj
##
from pathlib import Path
from glob import glob



##
from pathlib import Path
from glob import glob
import rioxarray
#from utils.cog import write_cog


def paths_to_datetimeindex(paths):
    string_slice=(45,-5) #string_slice=(45,60)
    date_strings = [os.path.basename(i)[slice(*string_slice)]
                    for i in paths]
    return pd.to_datetime(date_strings)


def unzip(zipped_filename):
    with zipfile.ZipFile(zipped_filename, 'r') as zip_ref:
        if not os.path.exists('unzipped'):
            os.makedirs('unzipped')
        zip_ref.extractall('./unzipped')

if not os.path.exists('unzipped'):
    os.makedirs('unzipped')


def queryS2(file):
    """Read an input product list returning the full-path product list suitable for reading datasets.

    Parameters:
        file (str): full-path of the input file listing target products

    Return: S5P L2 full-path to files (list)
    """
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
    products = []
    for item in list:
        if item.endswith('.zip') or item.endswith('.SAFE') :
            products.append(item)
        else:
            for file in Path(item).rglob('*.zip') or Path(item).rglob('*.SAFE') :
                products.append(str(file))
    return products


def product_level(item):
    """Check for S2 product type. This information will change the relative path to images.

    Parameters:
        item (str): full path to S2 products location

    Return: exit status (bool)
    Raise ValueError for Unrecognized product types
    """
    if "MSIL2A" in item:
        return True
    elif "MSIL1C" in item:
        return False
    else:
        raise ValueError("%s: Unrecognized S2 product type"%item)



def bands(item,res='10m'):
    """Search for target MSIL2A bands given an input resolution. This is useful for index computations.

    Parameters:
        item (str): full path to S2 products location
        res (str): resolution of S2 images; default set to `10m`; allowed options: `10m`,`20m`,`60m`

    Return: bands sorted by increasing wavelength (list)
    """
    msi = product_level(item)
    products = []
    string = '*_'+str(res)+'.jp2'
    if msi: # L2A
        for path in Path(item).rglob(string):
            products.append(str(path))
    else: # L1C
        for path in Path(item).rglob('*.jp2'):
            products.append(str(path))
    return sorted(products) # ordered bands


def sclbands(item):
    """Search for target MSIL2A bands given an input resolution. This is useful for index computations.

    Parameters:
        item (str): full path to S2 products location
        res (str): resolution of S2 images; default set to `10m`; allowed options: `10m`,`20m`,`60m`

    Return: bands sorted by increasing wavelength (list)
    """
    msi = product_level(item)
    products = []
    #string = '*_'+str(res)+'.jp2'
    if msi: # L2A
        for path in Path(item).rglob('*_SCL_*'):
            products.append(str(path))
    #else: # L1C
        #for path in Path(item).rglob('*.jp2'):
            #products.append(str(path))
    return sorted(products) # ordered bands

epsg = {'init': 'EPSG:4326'}
def affine(b):
    """Compute an affine coordinates reprojection using rasterio python package, given an EPSG init argument

    Parameters:
        b (str): full path to a S2 `.jp2` file

    Return: longitude, latitude (numpy arrays)
    """
    # S2 bands share the same geometry
    ds = xarray.open_rasterio(b).isel(band=0)
    ra = rasterio.open(b,driver='JP2OpenJPEG')
    # affine transformation to lat and lon
    xt, yt = rasterio.warp.transform(src_crs=ra.crs, dst_crs=rasterio.crs.CRS(epsg), xs=ds.x,ys=ds.y)
    lon, lat = np.array(xt), np.array(yt)
    return lon,lat




ARG=json.load(open("vlabparams.json","r"))

print(str(ARG['bbox'][0])) #1
print(str(ARG['bbox'].split(","))) #['19.1031', ' 64.0410', ' 19.8981', '64.4038']

print(str(ARG['bbox'])) #19.1031, 64.0410, 19.8981,64.4038
lon_min=ARG['bbox'].split(",")[0]
lat_min=ARG['bbox'].split(",")[1]
lon_max=ARG['bbox'].split(",")[2]
lat_max=ARG['bbox'].split(",")[3]


print(str(lon_min))
print(lat_min)
print(lon_max)

proj_wgs84 = pyproj.Proj(init="epsg:4326")
proj_gk4 = pyproj.Proj(init="epsg:32632")   #EPSG:32632
x_min, y_min = pyproj.transform(proj_wgs84, proj_gk4, lon_min, lat_min)
x_max, y_max = pyproj.transform(proj_wgs84, proj_gk4, lon_max, lat_max)
print(x_min)
print(y_min)
print(x_max)
print(y_max)

#---
#download_unzipped_path = os.path.join(os.getcwd(), 'unzipped')
download_unzipped_path = os.path.join(os.getcwd(), 'data')

listfiles =[]
for item in os.listdir(download_unzipped_path):
    file_names = os.path.join(download_unzipped_path, item)
    listfiles.append(file_names)


files = os.listdir(download_unzipped_path)
print(files)


time_var = xr.Variable('time', paths_to_datetimeindex(files))
print(time_var)

red =[bands(file,res='10m')[3]  for file in listfiles]
#print(red)
nir = [bands(file,res='10m')[4]  for file in listfiles]
#print(nir)

redlist = red
nirlist = nir


#window
#window10= rasterio.windows.Window(0,0, 1080,1080)
#window60= rasterio.windows.Window(0,0, 1080/6,1080/6)


nir_da_gran = xr.concat([xr.open_rasterio(i,chunks={'x':512, 'y':512}) for i in nirlist],
#nir_da_gran = xr.concat([xr.open_rasterio(i) for i in nirlist],
                        dim=time_var)  #[:,:,0:20,0:20]


mask_lon = (nir_da_gran.x >= x_max) & (nir_da_gran.x <= x_min)   #   429770.327 4666780.373
mask_lat = (nir_da_gran.y >= y_max) & (nir_da_gran.y <= y_min)

nir_da = nir_da_gran.where(mask_lon & mask_lat, drop=True)

#nir_ds = nir_da_gran.rio.isel_window(window10).to_dataset('band')
nir_ds = nir_da.to_dataset('band')
nir_ds = nir_ds.rename({1: 'nir'})
nir_ds = nir_ds.astype('int16')
print(nir_ds)

red_da_gran = xr.concat([xr.open_rasterio(i,chunks={'x':512, 'y':512}) for i in redlist],
#red_da_gran = xr.concat([xr.open_rasterio(i) for i in redlist],
                        dim=time_var)

mask_lon = (red_da_gran.x >= x_max) & (red_da_gran.x <= x_min)
mask_lat = (red_da_gran.y >= y_max) & (red_da_gran.y <= y_min)
red_da = red_da_gran.where(mask_lon & mask_lat, drop=True)

red_ds = red_da.to_dataset('band')
#red_ds = red_da_gran.rio.isel_window(window10).to_dataset('band')
red_ds = red_ds.rename({1: 'red'})#[:,:,0:500,0:500]
red_ds = red_ds.astype('int16')
print(red_ds)


scl = []
for file in listfiles:
    scl_list = sclbands(file)[1]     #dp2.sclbands(file)[0]  sclbands(file)[1]
    print(scl_list)
    scl.append(scl_list)

scl_da_gran = xr.concat([xr.open_rasterio(i) for i in scl],  #chunks={'x':512, 'y':512}
                        dim=time_var)

mask_lon = (scl_da_gran.x >= x_max) & (scl_da_gran.x <= x_min)   #   429770.327 4666780.373
mask_lat = (scl_da_gran.y >= y_max) & (scl_da_gran.y <= y_min)

scl_da = scl_da_gran.where(mask_lon & mask_lat, drop=True)

#scl_ds = scl_da_gran.rio.isel_window(window60).to_dataset('band')
scl_ds = scl_da.to_dataset('band')

scl_ds = scl_ds.rename({1:'scl'})
print(scl_ds)

#scl_ds_int = scl_ds.interp(y=red_ds["y"], x=red_ds["x"])
#scl_ds_int= scl_ds_int.astype('int16')
#print(scl_ds_int)

#ds=xr.merge([nir_ds,red_ds,scl_ds_int])
ds=xr.merge([nir_ds,red_ds,scl_ds])
ds =ds.astype('int16')
print('ds')
print(ds.info())



#print(ds.red.attrs)
ndvi = ((ds['nir'] - ds['red'])/(ds['nir'] + ds['red']))
print(ndvi)
#print('ndvi[1,1,1]')
#print(ndvi.values[1,1,1])

#print(ndvi.isel(time=0))
#write_cog(nir_ds.isel(time=0).to_array().compute(), "ndvic.tif")

scl = ds['scl']
good_data = scl.where((scl == 4) | (scl == 5) | (scl == 6))
#print(good_data)
ndvi_no_cloud = ndvi.where(good_data>=5)  #ndvi
#ndvi_no_cloud

##Plot _output
#ndvi.isel(time=0).rio.to_raster("ndvi_0.tif")
ndvi.rio.to_raster('ndvi_output.tif', dtype="float32")

mask = ndvi.isnull()
#mask
ndvi_cl = ndvi.where(~mask, other=0)
print(ndvi_cl)

#Plot output
ndvi.rio.to_raster('ndvi_cl_output.tif', dtype="float32")


# vPOS = Value at peak of season:
vPOS = ndvi_cl.max("time").values

# POS = DOY of peak of season
#dvi_cl.isel(time=ndvi_cl.argmax("time")).time.dt.dayofyear.values
#using chunks
computed_ndvi_cl = ndvi_cl.load()
type(computed_ndvi_cl.data)
computed_ndvi_cl
ndvi_cl.isel(time=computed_ndvi_cl.argmax("time")).time.dt.dayofyear.values

# Trough = Minimum value
ndvi_cl.min("time").values

# AOS = Amplitude of season
(ndvi_cl.max("time")-ndvi_cl.min("time")).values


   
    


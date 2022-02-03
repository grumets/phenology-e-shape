import os,sys
from pathlib import Path
from glob import glob

##
#import urllib.request
# connect to the API
import datetime
import zipfile
import xarray as xr
import pandas as pd
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
api = SentinelAPI('user', 'password', 'https://scihub.copernicus.eu/dhus')
import rioxarray
import json

fileBbox = read_geojson(bboxgeo)
ARG=json.load(open("vlabparams.json","r"))

print(str(ARG))
arg=""
for k,v in ARG.items():
    if (v is False)|(v in ["False","false","F"]):
        continue
    else:
        if (v is True)|(v=="true"):
            #v=""
            v="true"
        arg+=" -- "+" ".join([k,str(v)])
print(arg)

dates =[ARG['data1'],ARG['data2']]

footprint = geojson_to_wkt(read_geojson(bboxgeo))
products = api.query(footprint,
                     date = (dates[0],dates[1]),
                     platformname = 'Sentinel-2',
                     processinglevel = 'Level-2A',
                     cloudcoverpercentage = (0, 80))  #80%


print(len(products))

for i in products:
    print (i,api.get_product_odata(i)['title'])
    #print (api.get_product_odata(i)['url'])

output = "output.txt"
with open(output, "w") as outputfile:
    outputfile.write(len(products))


products_df = api.to_dataframe(products)
# sort and limit to first X sorted products
products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
products_df_sorted = products_df_sorted.head()
# download sorted and reduced products
#api.download_all(products_df_sorted.index)  #donwload products

if not os.path.exists('temp'):
    os.makedirs('temp')

download_path = './temp'
api.download_all(products_df_sorted.index,directory_path=download_path)

ds = products_df['title'].to_xarray()  #xarray.DataArray


def unzip(zipped_filename):
    with zipfile.ZipFile(zipped_filename, 'r') as zip_ref:
        if not os.path.exists('unzipped'):
            os.makedirs('unzipped')
        zip_ref.extractall('./unzipped')

if not os.path.exists('unzipped'):
    os.makedirs('unzipped')


download_unzipped_path = os.path.join(os.getcwd(), 'unzipped')


extension = ".zip"
for item in os.listdir(download_path):
    print(item)
    if item.endswith(extension): # check for ".zip" extension
        file_name = os.path.join(download_path, item) # get full path of files
        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
        zip_ref.extractall(download_unzipped_path) # extract file to dir
        zip_ref.close() # close file


files = os.listdir(download_unzipped_path)
print(files)

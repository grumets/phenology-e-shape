import os,sys
#import urllib
#from urllib import request

##
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
api = SentinelAPI('iserra', 'Creaf-21', 'https://scihub.copernicus.eu/dhus')
import rioxarray
import json

#fileBbox = bboxgeo   #geojosn file closed linestring

#bboxgeo = 'bboxgeo.json'
#bboxgeo = sys.argv[1]

#fileTemporal = sys.argv[2]   #txt file

fileBbox = read_geojson(bboxgeo)
ARG=json.load(open("vlabparams.json","r"))

"""
bboxgeo
{'data1': '20210101', 'data2': '20211231', 'bbox': 'false'}
-- data1 20210101 -- data2 20211231
"""

print(str(ARG)) #f
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
#print(str(ARG['bbox'].split(","))) #[false]

#print(str(ARG['bbox'])) #19.1031, 64.0410, 19.8981,64.4038
#dates[0]=ARG['bbox'].split(",")[0]
#dates[1]=ARG['bbox'].split(",")[1]

dates =[ARG['data1'],ARG['data2']]
print(dates[0])
print(dates[1])

footprint = geojson_to_wkt(fileBbox)
#footprint = geojson_to_wkt(read_geojson(fileBbox))

print(footprint)
"""
with open(fileTemporal) as f:
#with open('input/dates.txt') as f:
    contents = f.read()
    dates = contents.split(",")
    print(dates)
"""
#print(arg[0])
#print(dates[1])

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

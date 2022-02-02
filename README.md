# phenology-e-shape
Phenological product generation from Sentinel 2 in ODC, ONDA-DIAS and VLAB.

The code aims to generate a best practice to calculate vegetation phenology measurements following these points:
- Load Sentinel-2 data for an area of interest and time range.
- Calculate a vegetation index (NDVI).
- Generate a zonal time series.
- Calculate phenology products: dormancy, greenup, maturity, senescence

The code is written in Python and
requires the following packages: rasterio, rioxarray, numpay.
In odc and dias folder: the code is written using Jupyter notebooks.
Vlab folder:  python script and the specific folder and files to be executed through the virtual laboratory: https://vlab.geodab.eu/

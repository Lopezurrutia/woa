import numpy as np
import pandas as pd
## Instalar iris y oceans:
# conda install -c conda-forge iris
# pip install oceans
## modified from woa_profile to select also depth
## see https://github.com/ocefpaf/python-oceans/blob/master/oceans/datasets.py for documentation on source code
import iris
import warnings
from oceans.datasets import _woa_url
from oceans.datasets import _woa_variable
def woa_point(lons, lats, depths,variable='temperature', time_period='annual', resolution='1/4'):
   #  variables:
   #      'temperature': 't',
   #      'salinity': 's',
   #      'silicate': 'i',
   #      'phosphate': 'p',
   #      'nitrate': 'n',
   #      'oxygen_saturation': 'O',
   #      'dissolved_oxygen': 'o',
   #      'apparent_oxygen_utilization': 'A',
   # time_periods:
   #      'annual': '00',
   #      'january': '01',
   #      'february': '02',
   #      'march': '03',
   #      'april': '04',
   #      'may': '05',
   #      'june': '06',
   #      'july': '07',
   #      'august': '08',
   #      'september': '09',
   #      'october': '10',
   #      'november': '11',
   #      'december': '12',
   #      'winter': '13',
   #      'spring': '14',
   #      'summer': '15',
   #      'autumn': '16',
   # resolutions:
   #  '5': ('5deg', '5d'),
   #  '1': ('1.00', '01'),
   #  '1/4': ('0.25', '04'),
        
    url = _woa_url(variable=variable, time_period=time_period, resolution=resolution)
    print(url)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cubes = iris.load_raw(url)

    # TODO: should we be using `an` instead of `mn`?
    # an=Objectively analyzed climatologies are the objectively interpolated mean fields for oceanographic variables at standard depth levels for the World Ocean.
    # mn=The statistical mean is the average of all unflagged interpolated values at each standard depth level for each variable in each 1° square which contains at least one measurement for the given oceanographic variable.
    
    v = _woa_variable(variable)
    cube = [c for c in cubes if c.var_name == f'{v}_an'][0]

    ## This version is very slow, using the same approach as woa_profile
    # scheme = iris.analysis.Nearest()
    # sample_points = [('longitude', lon), ('latitude', lat), ('depth', depth)]
    # kw = {
    #     'sample_points': sample_points,
    #     'scheme': scheme,
    #     'collapse_scalar': True
    # }

    # return cube.interpolate(**kw)

    
    def nearval(depth,lat,lon):
        index1=cube.coord('depth').nearest_neighbour_index(depth)
        index2=cube.coord('latitude').nearest_neighbour_index(lat)
        index3=cube.coord('longitude').nearest_neighbour_index(lon)
        print(cube.shape,index1,index2,index3)
        return cube[0,index1,index2,index3].data

    ##
    if (len(set(len(x) for x in [lons,lats,depths])) != 1):
        raise ValueError(" lat, lon and depths should be equal length")

    output=np.empty(len(lons))

    for i, (depth,lat,lon) in enumerate(zip(depths,lats,lons)):
        print(i)
        print(depth,lat,lon)
        output[i]=nearval(depth,lat,lon)
        print(output[i])

    return output

## Example on how to use:
aa=woa_point(lons=[-10], lats=[45] ,depths=[0], time_period='00')
## This works with multiple data points
aa=woa_point(lons=[-10,-12],lats=[45,47],depths=[0,0], time_period='00')

aa=woa_point(lons=[10,-12,30],lats=[45,47,-44],depths=[0,10,100], time_period='01')




lons_in=[10,-12,30]                                                               
lats_in=[45,47,-44]                                                               
depths_in=[0,10,100]                                                              
months_in=[1,1,1]       

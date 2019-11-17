import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap

import numpy as np
import pandas as pd

import argparse
import os

parser = argparse.ArgumentParser()
arg = parser.add_argument
arg('--variable', default="temperature")
arg('--resolution', default='04')
arg('--field', default='an')
arg('--csv', default='csvdata.csv')
arg('--woapath', default='woa_np/')
args = parser.parse_args()




def make_plot(lons,lats,mat_data,min_val,max_val,titulo,filename=None):
    m = Basemap(projection='robin',lon_0=0)
    m.drawcoastlines()
    m.fillcontinents()
    lon2d, lat2d = np.meshgrid(lons, lats)
    # Transforms lat/lon into plotting coordinates for projection
    x, y = m(lon2d, lat2d)

    # x_a, y_a = m(woa_s['lon'].values,woa_s['lat'].values)
    # m.scatter(x_a,y_a,marker='o',color='k')

    Zm = np.ma.masked_where(np.isnan(mat_data),mat_data)
    cs = m.pcolormesh(x, y, Zm,vmin=min_val,vmax= max_val)
    cbar=m.colorbar(cs,location='bottom',pad= "5%")
    cbar.set_label(titulo)                   
    if filename:
        plt.savefig(filename)
                   



# Reads WOA numpy array and calls make global plot for a given month and depth 
def read_and_plot(
        variable='temperature',
        resolution = '04',
        woapath='woa_np/',
        month=0,
        depthlevel=0,
        min_val=-5,
        max_val=35,
        title= 'Sea surface temperature',
        filename='sst_jan.png'):
    ## Reads the WOA numpy matrix and depth, lat, lon vectors
    outfile = f'woa18_{variable}_{resolution}.npz'
    outfile = os.path.join(woapath,outfile)
    temp_mat = np.load(outfile)#var=woa_mat,lats=lats,lats_bnds=lats_bnds,lons=lons,lons_bnds=lons_bnds,depths=depths,depths_bnds=depths_bnds)

    data = temp_mat['var']
    depths=temp_mat['depths']
    depths_bnds=temp_mat['depths_bnds']
    lons=temp_mat['lons']
    lons_bnds=temp_mat['lons_bnds']
    lats=temp_mat['lats']
    lats_bnds=temp_mat['lats_bnds']

    make_plot(lons,lats,data[month,depthlevel,:,:],min_val = min_val,max_val=max_val,titulo = title,filename=filename)
    return


def extract_woa(
        lons, ## array or list with lons
        lats, ## array or list with lats
        depths=None, ## if None, depth profile is extracted
        months= None, ## if None, seasonal cycle is extracted
        variable='temperature',
        resolution = '04',
        woapath='woa_np/'):

    lons=np.asarray(lons)
    lats=np.asarray(lats)
        
    if months is not None:
        months=np.asarray(months)
        if((months>11.).any() or (months < 0.).any()):
            print('Month should be 0 to 11')
            return
    
    lons = np.mod(lons + 180.0, 360.0) - 180.0 ## convert 0-360 to -180 to 180
    if((lons>180.).any() or (lons < -180.).any()):
        print('Longitudes should be -180 to 180 or 0 to 360')
        return

    if((lats>90.).any() or (lats < -90.).any()):
        print('Latitudes should be -90 to 90')
        return

        
    ## Reads the WOA numpy matrix and depth, lat, lon vectors
    outfile = f'woa18_{variable}_{resolution}.npz'
    outfile = os.path.join(woapath,outfile)
    temp_mat = np.load(outfile)#var=woa_mat,lats=lats,lats_bnds=lats_bnds,lons=lons,lons_bnds=lons_bnds,depths=depths,depths_bnds=depths_bnds)

    data = temp_mat['var']
    depths_woa=temp_mat['depths']
    depths_bnds=temp_mat['depths_bnds']
    if depths is not None:
        depths=np.asarray(depths)
        if((depths<0.).any()):
            print('Negative depths converted to positive should be 0 to 11')
            depths=abs(depths) ## convert negative depths to positive

        if((depths> max(depths_bnds[:,1])).any()):
            print('Depths should be smaller than',max(depths_bnds[:,1]))
            print('Deeper values are clipped to ',max(depths_bnds[:,1]))
            depths[depths> max(depths_bnds[:,1])]= max(depths_bnds[:,1])

    lons_woa=temp_mat['lons']
    lons_bnds=temp_mat['lons_bnds']
    lats_woa=temp_mat['lats']

    lats_bnds=temp_mat['lats_bnds']
    ## Get the bins from provided locations
    lats_index=np.digitize(lats,lats_bnds[:,1],right=True)
    lons_index=np.digitize(lons,lons_bnds[:,1],right=True)

    if months is None:
        months_index= slice(0,None)
    else:
        months_index=np.digitize(months,np.arange(1,13),right=True)

    if depths is None:
        depths_index= slice(0,None)
    else:
        depths_index=np.digitize(depths,depths_bnds[:,1],right=True)
    data_selection=data[months_index,depths_index,lats_index,lons_index]
    return data_selection

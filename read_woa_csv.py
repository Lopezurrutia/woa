import numpy as np
import pandas as pd
import tempfile
import gzip
import shutil
import wget

# ###############################################################
# ## Previous versions required data to be downloaded first to a folder

# wget -N -nH -nd -r -e robots=off --no-parent --force-html -A.nc https://data.nodc.noaa.gov/woa/WOA18/DATA/temperature/csv/decav/0.25/
# wget -N -nH -nd -r -e robots=off --no-parent --force-html -A.nc https://data.nodc.noaa.gov/woa/WOA18/DATA/salinity/csv/decav/0.25/

# ## Could also be done with bash script
# #!/bin/bash
# # t1='https://data.nodc.noaa.gov/woa/WOA18/DATA/temperature/csv/decav/0.25/woa18_decav_t'
# # t1_b="woa18_decav_t"
# # t3="an04.csv.gz"
# # for i in $(seq -f "%02g" 2 12);
# # do
# #     wget $t1$i$t3
# #     gunzip $t1_b$i$t3
# # done


def _woa_variable(variable):
    _VAR = {
        'temperature': 't',
        'salinity': 's',
        'silicate': 'i',
        'phosphate': 'p',
        'nitrate': 'n',
        'oxygen_saturation': 'O',
        'dissolved_oxygen': 'o',
        'apparent_oxygen_utilization': 'A',
    }
    v = _VAR.get(variable)
    if not v:
        raise ValueError(
            f'Unrecognizable variable. Expected one of {list(_VAR.keys())}, got "{variable}".'
        )
    return v

grids = {
    '5': ('5deg', '5d'),
    '1': ('1.00', '01'),
    '1/4': ('0.25', '04'),
}


def read_woa(variable='temperature',resolution='1/4',field='an'):
    print(field)
    grid = grids.get(resolution)
    woa_mat = np.zeros((len(lats_intervals),len(lons_intervals),len(woa_depths),len(month_intervals)))
    for i in np.arange(12):
        print('Reading month',i)
        ## Create the woa url to download
        baseurl='https://data.nodc.noaa.gov/woa/WOA18/DATA/'
        baseurl=f'{baseurl}{variable}/csv/decav/{grid[0]}/'
        suf = 'woa18_decav_'
        woa_file = '{suf}{var}{foo:02d}{field}{ress}.csv'.format(foo=i,var= _woa_variable(variable),suf=suf,pref=pref,field=field,ress=grid[1])
        woa_url = f'{baseurl}{woa_file}.gz'



        ## Download de WOA file as a temporary file
        with tempfile.TemporaryDirectory() as tmpdirname:
            print('created temporary directory', tmpdirname)
            ftemp=f'{tmpdirname}/WOA.gz'
            print('Beginning file download with urllib2...')
            wget.download(woa_url, ftemp)
            print('downloaded to ',ftemp)
            ftemp_csv=f'{tmpdirname}/WOA.csv'
            ## uncompress the gzip csv file
            with gzip.open(ftemp, 'rb') as f_in:
                with open(ftemp_csv, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            ## Read and reshape csv file
            woa_s = pd.read_csv(ftemp_csv,skiprows= 2,header=None,na_values='',names=['lat','lon'] +woa_depths)

            woa_s['lat_bins'] = pd.cut(woa_s['lat'],bins=lats_intervals)
            woa_s['lon_bins'] = pd.cut(woa_s['lon'],bins=lons_intervals)
            res= woa_s.groupby(['lat_bins','lon_bins']).mean()
            ##res.drop(['lat','lon'],inplace=True)

            res_np = res.values
            res_np = res_np[:,2:]
            # mat_data = np.reshape(res[5].values,(len(lats_intervals),len(lons_intervals)))
            woa_mat[:,:,:,i] = np.reshape(res_np,(len(lats_intervals),len(lons_intervals),len(woa_depths)))
    return woa_mat


##############################################
## Recreate WOA intervals for binning

woa_depths = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500,550,600,650,700,750,800,850,900,950,1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1500]

woa_depths_lefts = [-5,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500,550,600,650,700,750,800,850,900,950,1000,1050,1100,1150,1200,1250,1300,1350,1400,1450]
woa_depths_rights = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500,550,600,650,700,750,800,850,900,950,1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1500,1550]

depth_intervals = pd.IntervalIndex.from_arrays((np.array(woa_depths)+np.array(woa_depths_lefts))/2.,(np.array(woa_depths)+np.array(woa_depths_rights))/2.)
month_intervals = pd.interval_range(start=0.5, end=12.5,freq=1)
##############################################


## Lat lon bins depend on grid size
grid_size = 0.25
lats_intervals = pd.interval_range(start=-90, end=90,freq=grid_size)
lons_intervals = pd.interval_range(start=-180, end=180,freq=grid_size)
    
temp_mat = read_woa(variable='temperature',resolution='1/4',field='an'
)
sal_mat = read_woa(suf = './data/woa18_decav_s',
         pref = 'an04.csv')



## Roll axis so it has same dimensions as netcdf
temp_mat=np.rollaxis(temp_mat,3,0)
temp_mat=np.rollaxis(temp_mat,3,1)


## Roll axis so it has same dimensions as netcdf
sal_mat=np.rollaxis(sal_mat,3,0)
sal_mat=np.rollaxis(sal_mat,3,1)

np.savez('data/woa_sal_04.npz',sal_mat)
np.savez('data/woa_temp_04.npz',temp_mat)

## How to read
sal_mat = np.load('data/woa_sal_04.npz')['arr_0']
temp_mat = np.load('data/woa_temp_04.npz')['arr_0']

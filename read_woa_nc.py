import numpy as np
import netCDF4
import argparse
import os

parser = argparse.ArgumentParser()
arg = parser.add_argument
arg('--variable', default="temperature")
arg('--resolution', default='04')
arg('--field', default='an')
arg('--outpath', default='woa_np/')
args = parser.parse_args()

def _woa_variable(variable):
    ## see https://github.com/ocefpaf/python-oceans/blob/master/oceans/datasets.py for documentation on source code
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


def _woa_url(variable, time_period, resolution):
    base = 'https://data.nodc.noaa.gov/thredds/dodsC'

    v = _woa_variable(variable)

    if variable not in ['salinity', 'temperature']:
        pref = 'woa09'
        warnings.warn(
            f'The variable "{variable}" is only available at 1 degree resolution, '
            f'annual time period, and "{pref}".'
        )
        return (
            f'{base}/'
            f'{pref}/'
            f'{variable}_annual_1deg.nc'
        )
    else:
        dddd = 'decav'
        pref = 'woa18'

    grids = {
        '5': ('5deg', '5d'),
        '1': ('1.00', '01'),
        '04': ('0.25', '04'),
    }
    grid = grids.get(resolution)
    if not grid:
        raise ValueError(
            f'Unrecognizable resolution. Expected one of {list(grids.keys())}, got "{resolution}".'
        )
    res = grid[0]
    gg = grid[1]

    time_periods = {
        'annual': '00',
        'january': '01',
        'february': '02',
        'march': '03',
        'april': '04',
        'may': '05',
        'june': '06',
        'july': '07',
        'august': '08',
        'september': '09',
        'october': '10',
        'november': '11',
        'december': '12',
        'winter': '13',
        'spring': '14',
        'summer': '15',
        'autumn': '16',
    }

    time_period = time_period.lower()
    if len(time_period) == 3:
        tt = [time_periods.get(k) for k in time_periods.keys() if k.startswith(time_period)][0]
    elif len(time_period) == 2 and time_period in time_periods.values():
        tt = time_period
    else:
        tt = time_periods.get(time_period)

    if not tt:
        raise ValueError(
            f'Unrecognizable time_period. '
            f'Expected one of {list(time_periods.keys())}, got "{time_period}".'
        )

    url = (
        f'{base}/'
        '/ncei/woa/'
        f'{variable}/decav/{res}/'
        f'{pref}_{dddd}_{v}{tt}_{gg}.nc'  # '[PREF]_[DDDD]_[V][TT][FF][GG]' Is [FF] used?
    )
    return url

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
   #  '04': ('0.25', '04'),
        

    # an=Objectively analyzed climatologies are the objectively interpolated mean fields for oceanographic variables at standard depth levels for the World Ocean.
    # mn=The statistical mean is the average of all unflagged interpolated values at each standard depth level for each variable in each 1° square which contains at least one measurement for the given oceanographic variable.

def main():
    ##########################################################
    ## grab the annual time period to get coordinate system
    print('Reading data for', args.variable, args.resolution)
    print('Getting matrix dimensions')
    url = _woa_url(variable=args.variable, time_period='00', resolution=args.resolution)
    nc_fid=netCDF4.Dataset(url, mode='r')  

    lats = nc_fid.variables['lat'][:]
    lats_bnds = nc_fid.variables['lat_bnds'][:]

    lons = nc_fid.variables['lon'][:]
    lons_bnds = nc_fid.variables['lon_bnds'][:]
    ## not too much data bellow 1500m, we limit depth to that
    ## remove [:57] if you want all depths
    depths = nc_fid.variables['depth'][:][:57]
    depths_bnds = nc_fid.variables['depth_bnds'][:][:57]
    nc_fid.close()
    ##########################################################
    months = np.arange(12)

    print('Creating np matrix to hold data')
    woa_mat = np.zeros((len(months),len(depths),len(lats),len(lons)))
    print('Matrix shape is:', woa_mat.shape)
    print('Lat dimension:', len(lats))
    print('Lon dimension:', len(lons))
    print('Depth dimension:', len(depths))


    for i in months:
        print('Reading month',i)
        time_period=str(i).zfill(2)
        url = _woa_url(variable=args.variable, time_period=time_period, resolution=args.resolution)
        print('url',url)
        nc_fid=netCDF4.Dataset(url, mode='r')  

        v = _woa_variable(args.variable)
        v = f'{v}_{args.field}'
        ## read, convert to nonmasked array, fill nas with np.nan
        ## not all nc have same depths ¿?
        month_data=nc_fid.variables[v][:]
        print('Read data matrix', month_data.shape)
        month_data = np.ma.filled(month_data,fill_value=np.nan)
        month_data = month_data[:,:len(depths),:,:]
        woa_mat[i,:,:,:] = month_data

        nc_fid.close()
        print('finished month',i)

    ## Writes the resulting matrix to 
    outfile=f'woa18_{args.variable}_{args.resolution}.npz'
    outfile=os.path.join(args.outpath,outfile)
    if not os.path.exists(args.outpath):
        os.makedirs(args.outpath)
    print('Writing result to',outfile)
    np.savez_compressed(outfile,var=woa_mat,lats=lats,lats_bnds=lats_bnds,lons=lons,lons_bnds=lons_bnds,depths=depths,depths_bnds=depths_bnds)
    print('Done')
    return

if __name__== "__main__":
  main()
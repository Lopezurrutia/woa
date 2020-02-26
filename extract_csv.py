import numpy as np
import pandas as pd
from utils import extract_woa

import argparse
import os
    
parser = argparse.ArgumentParser()
arg = parser.add_argument
arg('--variable', default="temperature")
arg('--resolution', default='1')
arg('--csv', default='csvs/csvdata.csv')
arg('--woapath', default='woa_np/')
args = parser.parse_args()



df = pd.read_csv(args.csv)

Lons=df['Lon'].values
Lats=df['Lat'].values


if 'Depth' in df:
    Depths=df['Depth'].values
else:
    Depths=None

if 'Month' in df:
    Months=df['Month'].values
elif 'Decimalday' in df:
    if 'Year' in df:
        Year=df['Year'].values.astype('int')
    else:
        Year=None
    Decimalday = df['Decimalday'].values
    ## Convert Decimal day to month
    from datetime import datetime, timedelta
    if Year is None:
        Year= [1999]*len(Decimalday)
    Dates= [np.nan if (np.isnan(i) or np.isnan(j)) else datetime(i-1, 12, 31)+timedelta(days=j) for i,j in zip(Year,Decimalday) ]
    Months = [i.month-1 if isinstance(i, datetime) else np.nan for i in Dates]
else:
    Months=None


if Depths is None and Months is None:
    raise ValueError(
            f'csv should contain at leats a column with Month or Depth'
        )
elif Months is None:
    full_mat=np.vstack((Lons,Lats,Depths))
elif Depths is None:
    full_mat=np.vstack((Lons,Lats,Months))
else:
    full_mat=np.vstack((Lons,Lats,Depths,Months))

## Select data with all variables
complete_rows=np.isfinite(full_mat).all(axis=0)
res_full = np.full([full_mat.shape[1]], np.nan)
Lons=Lons[complete_rows]
Lats=Lats[complete_rows]
if Months is not None:
    Months=Months[complete_rows]
if Depths is not None:
    Depths=Depths[complete_rows]

res=extract_woa(lons=Lons,
                lats=Lats,
                depths=Depths,
                months=Months,
                variable=args.variable,
                resolution = args.resolution,
                woapath=args.woapath)
    
if Months is None:
    for months in np.arange(12):
        res_full = np.full([full_mat.shape[1]], np.nan)
        res_full[complete_rows]=res[months,:]
        df[f'{args.variable}_{months}_{args.resolution}']=res_full
elif Depths is None:
    ## Get woa_depths, a bit slow to reload numpy array
    outfile = f'woa18_{args.variable}_{args.resolution}.npz'
    outfile = os.path.join(args.woapath,outfile)
    temp_mat = np.load(outfile)#var=woa_mat,lats=lats,lats_bnds=lats_bnds,lons=lons,lons_bnds=lons_bnds,depths=depths,depths_bnds=depths_bnds)
    depths_woa=temp_mat['depths']

    for i,depths in enumerate(depths_woa):
        res_full = np.full([full_mat.shape[1]], np.nan)
        res_full[complete_rows]=res[:,i]
        df[f'{args.variable}_{depths}_{args.resolution}']=res_full
else:
    res_full[complete_rows]=res
    df[f'{args.variable}{args.resolution}']=res_full

df.to_csv(f'{os.path.splitext(args.csv)[0]}_{args.variable}{args.resolution}.csv',index=False)
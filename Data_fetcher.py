from argopy import DataFetcher
import bitsea.basins.V2 as OGS
from bitsea.commons.mask import Mask
import seawater as sw
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse

parser = argparse.ArgumentParser(description="Script per generare figure da tabelle.")
parser.add_argument("--outdir", "-o", required=True,  help="Directory di output per le figure")
parser.add_argument("--year",   "-y", required=True,  help="Only single year is allowed")
parser.add_argument("--month",  "-m", required=True,  help="Single month (01..12)")
args = parser.parse_args()

OUTDIR   = args.outdir
YEAR   = str(args.year)
MONTH = str(args.month).zfill(2)
###
### AIM n1: select all the floats in the MEDSEA
###

#### Datafetcher isnt able to subset irregular shape (only rectangules are allowed)
#### solution to skip the issue is to intersect datafetcher and rectangule in bitsea with a function starting fetching medsea data 
# issue --> DataFetcher is too low erdap could crash

# Dynamic inputs
start_date = datetime(int(YEAR), int(MONTH), 1)
end_date   = start_date + relativedelta(months=1)

YYYY_MM_start = start_date.strftime("%Y-%m")
YYYY_MM_end   = end_date.strftime("%Y-%m")

OUTDIR        = os.path.join(args.outdir,YEAR)
MASKFILE      = '/g100_work/OGS_devC/Benchmark/SETUP/PREPROC/MASK/meshmask.nc'
os.makedirs(OUTDIR, exist_ok=True)

# Static inputs
box_med  = [-5,36,30,46, 0, 2000, YYYY_MM_start, YYYY_MM_end ]
VARLIST  = ['PO4','NO3','DIC','AT','pHT','SiOH4']
basin_objects = {
    "alb": OGS.alb,
    "swm1": OGS.swm1,
    "swm2": OGS.swm2,
    "nwm": OGS.nwm,
    "tyr1": OGS.tyr1,
    "tyr2": OGS.tyr2,
    "adr1": OGS.adr1,
    "adr2": OGS.adr2,
    "aeg": OGS.aeg,
    "ion1": OGS.ion1,
    "ion2": OGS.ion2,
    "ion3": OGS.ion3,
    "lev1": OGS.lev1,
    "lev2": OGS.lev2,
    "lev3": OGS.lev3,
    "lev4": OGS.lev4,
}

# standard expert or researchmode
# datails at :https://argopy.readthedocs.io/en/latest/user-guide/fetching-argo-data/user_mode.html#user-mode

ds    = DataFetcher(mode='standard', ds='bgc',params=['DOXY'] ).region(box_med).to_xarray()
#df    = DataFetcher(mode='standard').region(box).to_dataframe()

# for all basins calculate NN-vars
for Sub in basin_objects.keys():
    mask      = basin_objects[Sub].is_inside(ds['LONGITUDE'].values, ds['LATITUDE'].values)
    ds_basin  = ds.isel(N_POINTS=mask)
    if ds_basin['DOXY'].size == 0:
       print(f"No valid data to predict for ---> {Sub}")
       continue
    if ds_basin['DOXY'].shape[0] < 1:
       print(f"Not enough points in ---> {Sub}")
       continue
    try:
       NNvar     = ds_basin.argo.canyon_med.predict() 
    except Exception as e:
        print(f"Prediction failed for {Sub}: {e}")
        continue

    if len(NNvar['DOXY'].data) == 0 :
        print('No data in --->' + Sub)
        continue 
    density   = sw.dens(NNvar['PSAL'],NNvar['TEMP'] , NNvar['PRES'])
    for VAR in VARLIST:
        if VAR=='pHT':
            pass
        else:
            NNvar[VAR]= NNvar[VAR] * density/1000.
    NN_profiles= NNvar.argo.point2profile()

    # check on data type of attributes , converted in str if needed
    #eg Fetched_constraints:  [x=-5.00/36.00; y=30.00/46.00; z=0.0/2000.0;
    
    for k, v in list(NN_profiles.attrs.items()):
        try:
            NN_profiles.attrs[k] = str(v)
        except Exception as e:
            raise TypeError(f"Attributo '{k}' non serializzabile: valore={v}, errore={e}")
    # end check
    print('processed -->'  + Sub)
    MONTHstr  = str(args.month).zfill(2)
    ## all profiles in a sub-basin was saved in netcdf
    outfile   = os.path.join(OUTDIR,f"{Sub}_{MONTHstr}_NN_derived_vars.nc")
    NN_profiles.to_netcdf(outfile)




"""

import sys
sys.exit()

po4 = ds_basin.argo.canyon_med.predict('PO4')
po4_profiles= po4.argo.point2profile()

TheMask = Mask.from_file(MASKFILE)
zlevs=TheMask.zlevels
z_shallow = zlevs[zlevs < 2000]
ds_interp = po4_profiles.argo.interp_std_levels(z_shallow)

import matplotlib as mpl
import matplotlib.pyplot as plt
import cmocean

import sys
sys.exit('carol')


#
LIST_X=[] # sono 92 valori
TIME=[]
for iwmo, wmo in enumerate (ds_interp['PLATFORM_NUMBER'].values) :
    tmp = str(wmo) + '_' + str(ds_interp['CYCLE_NUMBER'].values[iwmo])
    LIST_X.append(tmp)
    tmp = ds_interp['TIME'].values[iwmo]
    date_str = np.datetime_as_string(tmp, unit='D')
    TIME.append(date_str)

PO4 = ds_interp['PO4'].values  # shape (92, 95)
PRES = ds_interp['PRES_INTERPOLATED'].values  # shape (95,)

df_final= pd.DataFrame(PO4).T
df_final.index= PRES
df_final.columns=TIME
mean_profile = df_final.mean(axis=1)


import matplotlib.pyplot as plt
import numpy as np
import cmocean

Y = Y.astype(float)
fig, (ax1, ax2) = plt.subplots(
    1, 2,
    figsize=(12,4),
    gridspec_kw={"width_ratios":[4,1]},
    sharey=True)

# --- SUBPLOT 1: CONTOURF ---
c = ax1.contourf(X, Y, Z, levels=50, cmap=cmocean.cm.haline)
plt.colorbar(c, ax=ax1, label='PO4 [µmol/kg]')

ax1.set_xticks(x)
ax1.set_xticklabels(df_final.columns, rotation=90, fontsize=8)

ax1.set_ylabel('Depth [m]')
ax1.set_xlabel('Profile (Platform_Cycle)')
ax1.set_title('PO4 profiles - Tyr2 basin')

ax1.invert_yaxis()


# --- SUBPLOT 2: P Mean ---
ax2.plot(mean_profile.values, mean_profile.index, '-o', markersize=3)

ax2.grid(
    True,
    which='both',
    linestyle='--',
    linewidth=0.5,
    color='lightgray'
)

ax2.set_xlabel('PO4 [µmol/kg]')
ax2.set_title('Mean profile')


plt.tight_layout()
plt.savefig("PO4_contourf_and_meanprofile_Tyr2.png", dpi=150)
"""

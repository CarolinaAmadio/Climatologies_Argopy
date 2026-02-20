from argopy import DataFetcher
import bitsea.basins.V2 as OGS
from bitsea.commons.mask import Mask
import seawater as sw
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse
import sys 

parser = argparse.ArgumentParser(description="Script per generare figure da tabelle.")
parser.add_argument("--outdir", "-o", required=True,  help="Directory di output per le figure")
parser.add_argument("--year",   "-y", required=True,  help="Only single year is allowed")
parser.add_argument("--month",  "-m", required=True,  help="Single month (01..12)")
args = parser.parse_args()

OUTDIR   = args.outdir
OUTPUTDIR   = '/g100_scratch/userexternal/camadio0/ARGOPY_TESTS/Climatologies_Argopy/CANYON_MED_QCed'
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
params  = ['DOXY', 'NITRATE', 'CHLA','BBP700']
qc_vars = {var: f"{var}_ADJUSTED_QC" for var in params}
ds      = DataFetcher(mode='expert', ds='bgc',params=params ).region(box_med).to_xarray()
good = None
for var, qc_var in qc_vars.items():
    if qc_var in ds:
        mask = ds[qc_var].isin([1, 2, 5, 8])
        if good is None:
            good = mask
        else:
            good = good | mask   # OR logico: mantiene se almeno uno è valido

# Applica il filtro sul dataset
ds_qc = ds.where(good, drop=True)
rename_dict = {
    var: var.replace("NITRATE", "NITRATE_ins")
    for var in ds_qc.data_vars
    if "NITRATE" in var
}

ds_qc = ds_qc.rename(rename_dict)

for Sub in basin_objects.keys():
    mask      = basin_objects[Sub].is_inside(ds_qc['LONGITUDE'].values, ds_qc['LATITUDE'].values)
    if mask.sum() == 0: continue
    ds_basin = ds_qc.isel(N_POINTS=mask)
    if len(ds_basin.N_POINTS) <= 0: continue
    ds_basin = ds_basin.where(ds_basin.DIRECTION == 'A', drop=True)
    if len(ds_basin.N_POINTS) <= 0: continue
    if 'DOXY_ADJUSTED' in list(ds_basin): 
       NNvar = ds_basin.argo.canyon_med.predict()
       density   = sw.dens(NNvar['PSAL'],NNvar['TEMP'] , NNvar['PRES'])
       for VAR in VARLIST:
           if VAR=='pHT':
              pass
           else:
              NNvar[VAR]= NNvar[VAR] * density/1000.
       NN_profiles= NNvar.argo.point2profile()
       
    else:
       NN_profiles = ds_basin 
    for k, v in list(NN_profiles.attrs.items()):
        NN_profiles.attrs[k] = str(v)
    
    # da qui # 
    for i in range(NN_profiles.dims["N_PROF"]):

        prof = NN_profiles.isel(N_PROF=i)

        platform = str(int(prof.PLATFORM_NUMBER.values))
        cycle    = int(prof.CYCLE_NUMBER.values)

        # Nome directory
        outdir = os.path.join(OUTPUTDIR, platform)
        os.makedirs(outdir, exist_ok=True)
        outfile = os.path.join(outdir, f"SD{platform}_{cycle:03d}.nc")

        print("Writing:", outfile)


        # --- Encoding stile Argo ---
        encoding = {}
        for var in prof.data_vars:
            if np.issubdtype(prof[var].dtype, np.floating):
                encoding[var] = {
                    "_FillValue": 99999.0,
                    "zlib": True,
                    "complevel": 4
                }
        prof.to_netcdf(outfile, format="NETCDF4", encoding=encoding)


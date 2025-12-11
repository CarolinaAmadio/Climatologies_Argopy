from argopy import DataFetcher
import bitsea.basins.V2 as OGS
from bitsea.commons.mask import Mask

###
### AIM n1: select all the floats in the tyr sea.
### Reasons: the polygon in bit.sea is not squared
###

#### Datafetcher isnt able to subset irregular shape (only rectangules are allowed)
#### solution to skip the issue is to intersect datafetcher and rectangule in bitsea with a function

# es for tyr:
# 

## [lon_min, lon_max, lat_min, lat_max, pres_min, pres_max, tmin, tmax]:
#box     = [9.25, 16.5, 36.75, 41.25, 0, 2000, '2013-01', '2025-02'] #tyr2 box 
box_med = [-5,36,30,46, 0, 2000, '2013-01', '2025-01']

MASKFILE='/g100_work/OGS_devC/Benchmark/SETUP/PREPROC/MASK/meshmask.nc'
# standard expert or researchmode
# datails at :https://argopy.readthedocs.io/en/latest/user-guide/fetching-argo-data/user_mode.html#user-mode

ds    = DataFetcher(mode='standard', ds='bgc',params=['DOXY'] ).region(box).to_xarray()
#df    = DataFetcher(mode='standard').region(box).to_dataframe()


# 
mask = OGS.tyr2.is_inside(ds['LONGITUDE'].values, ds['LATITUDE'].values)
ds_tyr2 = ds.isel(N_POINTS=mask)

po4 = ds_tyr2.argo.canyon_med.predict('PO4')
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


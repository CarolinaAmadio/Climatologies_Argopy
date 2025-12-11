import os
import urllib.request

# This script downloads the required canyon-med dependency files
# into the Python environment where argopy is installed.
# Use it if argopy is installed but the canyon-med weight files are missing.

# path to download the canyon-med dependencies in my env
canyon_med_dir = os.path.expanduser(
    '~/envs/py38_seaborn/lib/python3.8/site-packages/argopy/static/assets/canyon-med/'
)

os.makedirs(canyon_med_dir, exist_ok=True)

# filelist
files = [
    'moy_phos_F.txt', 'std_phos_F.txt',
    'moy_doxy_F.txt', 'std_doxy_F.txt',
    'moy_chla_F.txt', 'std_chla_F.txt',
    'moy_no3_F.txt', 'std_no3_F.txt',
    'moy_no2_F.txt', 'std_no2_F.txt',
    'moy_nh4_F.txt', 'std_nh4_F.txt'
]

base_url = 'https://raw.githubusercontent.com/euroargodev/argopy/master/argopy/static/assets/canyon-med/'

for f in files:
    local_path = os.path.join(canyon_med_dir, f)
    if not os.path.exists(local_path):
        print(f'Downloading {f}...')
        urllib.request.urlretrieve(base_url + f, local_path)
    else:
        print(f'{f} already exists')

print("files are ready for canyon-med ")


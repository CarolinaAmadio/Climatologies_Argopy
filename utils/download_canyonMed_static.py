import os
import shutil
import subprocess

# This script downloads the entire "assets" folder from argopy GitHub
# into the Python environment where argopy is installed.

# Path to your Python environment
venv_dir = os.path.expanduser('~/envs/py38_seaborn')
assets_dir = os.path.join(venv_dir, 'lib/python3.8/site-packages/argopy/static/')
target_assets_dir = os.path.join(assets_dir, 'assets')

os.makedirs(assets_dir, exist_ok=True)

# Temporary directory to clone the repo
tmp_dir = '/tmp/argopy_tmp'

# Clone the argopy repo
if not os.path.exists(tmp_dir):
    print("Cloning argopy repository...")
    subprocess.run(['git', 'clone', '--depth', '1',
                    'https://github.com/euroargodev/argopy.git', tmp_dir], check=True)
else:
    print("Temporary repo already exists, pulling latest changes...")
    subprocess.run(['git', '-C', tmp_dir, 'pull'], check=True)

# Copy the entire assets folder
src_assets = os.path.join(tmp_dir, 'argopy/static/assets')
if os.path.exists(src_assets):
    if os.path.exists(target_assets_dir):
        print("Removing existing assets folder...")
        shutil.rmtree(target_assets_dir)
    print("Copying assets folder into environment...")
    shutil.copytree(src_assets, target_assets_dir)
else:
    print("assets folder not found in repository!")

# Clean up temporary clone
shutil.rmtree(tmp_dir)

print("All assets are ready in your Python environment!")


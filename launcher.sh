#!/bin/bash

#SBATCH --job-name=NN_Argopy
#SBATCH -N1 -n 1
#SBATCH --time=01:00:00
#SBATCH --account=OGS23_PRACE_IT
#SBATCH --partition=g100_all_serial

# Activate the Python virtual environment
source /g100/home/userexternal/camadio0/envs/py38_seaborn/bin/activate

# add bitsea to the PYTHONPAH
export PYTHONPATH=/g100_scratch/userexternal/camadio0/ARGOPY_TESTS/bit.sea/src:$PYTHONPATH

python Data_fetcher.py

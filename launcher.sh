#!/bin/bash

#SBATCH --job-name=NN_Argopy
#SBATCH -N1 -n 1
#SBATCH --time=02:00:00
#SBATCH --account=OGS23_PRACE_IT
#SBATCH --partition=g100_all_serial

cd $SLURM_SUBMIT_DIR
. utils/profile.inc

# fetch data from coriolis 
# calculate NN-based profiles
# arrange them in 16 subbasins
# save them in OUTDIR
 save them in OUTDIR


echo "Job started at: $(date)"

# Activate the Python virtual environment
source /g100/home/userexternal/camadio0/envs/py38_seaborn/bin/activate

# add bitsea to the PYTHONPAH
export PYTHONPATH=/g100_scratch/userexternal/camadio0/ARGOPY_TESTS/bit.sea/src:$PYTHONPATH

OUTDIR=/g100_scratch/userexternal/camadio0/ARGOPY_TESTS/Climatologies_Argopy/CANYON_MED_vars_subs/
mkdir -p $OUTDIR

for YEAR in {2019..2026}; do
  for MONTH in {01..12}; do
    echo ""
    echo ""
    echo "Processing YEAR=${YEAR}, MONTH=${MONTH}"
    echo ""
    echo ""
    my_prex_or_die "python -u Data_fetcher.py -y ${YEAR} -m ${MONTH} -o ${OUTDIR}"
  done
done

#mv slurm*out $OUTDIR/$YEAR

echo "Job finished at: $(date)"


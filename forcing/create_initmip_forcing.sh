#!/bin/bash



# get user and platform-specific variables like working_dir, pismcodedir,
source set_environment.sh
runname=`echo $PWD | awk -F/ '{print $NF}'`
outdir=$working_dir/$runname

initmip_anomaly_file=/p/projects/pism/mengel/pism_input/initmip/initmip_initmip8km.nc

mkdir -v $outdir
python prepare_timedependent_forcing.py --forcing_file_path $outdir \
    --background_file $infile --initmip_anomaly_file $initmip_anomaly_file

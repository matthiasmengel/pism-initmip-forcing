#!/bin/bash

# set computer and user specific variables,
# this is sourced from the pism run script, so that
# the pism run script can be shared without effort.
# created by matthias.mengel@pik-potsdam.de

export pismcode_dir=/home/mengel/pism
export working_dir=/p/tmp/mengel/pism_out
export input_data_dir=/p/projects/pism/mengel/pism_input
export infile=$working_dir/pismpik_038_initmip08km_1263/snapshots_323000.000.nc
export pism_exec=./bin/pismr
export pism_mpi_do="srun -n"

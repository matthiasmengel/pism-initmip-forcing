## PISM Initmip Forcing

Small collection of scripts to prepare the INITMIP Antarctica experiment
with PISM. Find the scripts for creating the anomaly forcing in
[forcing](forcing) and the postprocessing scripts in [postprocess](postprocess).

### Usage

#### Forcing
Copy the files to your directory with PISM run scripts, adapt the paths in
`set_environment.sh`, especially the one for your PISM background file,
and run `create_initmip_forcing.sh`.

Be aware that this code has to be run for each model simulation, as
the background PISM state enters the forcing created here and differs between
simulations.

#### postprocess
If PISM extra files were written to separate files for each year, use
`merge_extra_files.py` to merge them.
Adapt `config.py` and run `postprocess_ts.py` and `postprocess_ex.py`.

### Structure
```
forcing/
  create_initmip_forcing.sh
  prepare_timedependent_forcing.py
  set_environment.sh
postprocess/
  merge_extra_files.py
  config.py
  postprocess_ex.py
  postprocess_ts.py
  ismip6vars.csv
  resources_ismip6.py
```

### License

This code is licensed under GPLv3, see the LICENSE.txt. See the commit history for authors.

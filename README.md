## PISM Initmip Forcing

Small collection of scripts to prepare the INITMIP Antarctica anomaly forcing
for PISM runs.

### Usage

Copy the files to your directory with PISM run scripts, adapt the paths in
`set_environment.sh`, especially the one for your PISM background file,
and run `create_initmip_forcing.sh`.

Be aware that this code has to be run for each model simulation, as
the background PISM state enters the forcing created here and differs between
simulations.

### Structure
```
create_initmip_forcing.sh
prepare_timedependent_forcing.py
set_environment.sh
```
### License

This code is licensed under GPLv3, see the LICENSE.txt. See the commit history for authors.

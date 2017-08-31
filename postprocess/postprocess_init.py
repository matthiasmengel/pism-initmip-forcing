""" Copy the first timestep of the control experiment to init files.
    Run postprocess_ex.py
"""
import os
import subprocess
import config; reload(config)
import resources_ismip6; reload(resources_ismip6)

experiment_dir = os.path.join(config.working_dir, config.experiment)
output_dir = os.path.join(experiment_dir,"postprocessed")

# use first timestep of ctrl experiment and save as init.
exp = "init"

ctrl_variable_dir = os.path.join(output_dir,"ctrl_"+config.resolution)
single_variable_dir = os.path.join(output_dir, "init_"+config.resolution)

if not os.path.exists(single_variable_dir):
    os.makedirs(single_variable_dir)

## get the variables needed for InitMIP
ismip6_vars_dict = resources_ismip6.get_ismip6_vars_dict('ismip6vars.csv', 2)

# ligroundf not available in PISM
ismip6_vars_dict.pop("ligroundf",None)

for m_var in ismip6_vars_dict.keys():

    ctrl_file = os.path.join(ctrl_variable_dir, m_var+"_"+config.project+"_ctrl.nc")
    final_file = os.path.join(single_variable_dir, m_var+"_"+config.project+"_init.nc")

    print('Preparing init file for variable {}'.format(m_var))

    cmd = "module load cdo && cdo -O selyear,2000 "+ctrl_file+" "+final_file
    print cmd
    subprocess.check_call(cmd, shell=True)


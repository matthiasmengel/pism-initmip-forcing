#!/usr/bin/env python
# Copyright (C) 2016 Andy Aschwanden (https://github.com/pism/pism-gris/blob/master/initMIP)
# Modified by Matthias Mengel and Torsten Albrecht for initMIP Antarctica 2017

import os
import numpy as np
import csv
import subprocess as sub
from netCDF4 import Dataset as CDF
import resources_ismip6; reload(resources_ismip6)
import config; reload(config)

experiment_dir = os.path.join(config.working_dir, config.experiment)
output_dir = os.path.join(experiment_dir,"postprocessed")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)


ismip6_vars_dict = resources_ismip6.get_ismip6_vars_dict('ismip6vars.csv', 1)
ismip6_to_pism_dict = dict((k, v.pism_name) for k, v in ismip6_vars_dict.iteritems())
pism_to_ismip6_dict = dict((v.pism_name, k) for k, v in ismip6_vars_dict.iteritems())

pism_copy_vars = [x for x in (ismip6_to_pism_dict.values())] #+ pism_stats_vars)]

# do not process tendligroundf, PISM does not have it as diagnostic
pism_copy_vars.remove("tendligroundf")

for exp in ["smb_bmelt","smb","bmelt","ctrl"]:

    print "###### processsing timeseries of experiment", exp

    infile = os.path.join(experiment_dir,"timeseries"+config.ts_naming[exp]+".nc")

    out_filename = 'scalar_{project}_{exp}.nc'.format(
        project=config.project, exp=config.initmip_naming[exp])

    initmip_out_dir = os.path.join(output_dir,
        config.initmip_naming[exp]+"_"+config.resolution)

    if not os.path.exists(initmip_out_dir):
        os.makedirs(initmip_out_dir)

    infile_ismip6 = os.path.join(output_dir,"timeseries_ismip6_"+exp+".nc")
    initmipvars_file = os.path.join(output_dir,"timeseries_ismip6vars_"+exp+".nc")
    out_file = os.path.join(initmip_out_dir, out_filename)

    try:
        os.remove(out_file)
    except OSError:
        pass


    print "Prepare PISM output for ismip6 compatibility and save as '{}'".format(infile_ismip6)
    ncks_cmd = ['ncks', '-O', '-4', '-L', '3',
             infile,
             infile_ismip6]
    sub.call(ncks_cmd)

    #"total over ice domain of top surface ice mass flux = sub_shelf_ice_flux + grounded_basal_ice_flux" ;
    print "  Add variable 'tendlibmassbf'"
    ncap2_cmd = ['ncap2', '-O', '-s',
            'tendlibmassbf = sub_shelf_ice_flux + grounded_basal_ice_flux',
            infile_ismip6,
            infile_ismip6]
    sub.call(ncap2_cmd)


    # Check if request variables are present
    nc = CDF(infile_ismip6, 'r')
    for m_var in pism_copy_vars:
        if m_var not in nc.variables:
            print("Requested variable '{}' missing".format(m_var))
    nc.close()

    print(' Transfer pism_copy_vars to {}'.format(out_file))
    cmd = 'ncks -O -v '+','.join(pism_copy_vars)+" "+infile_ismip6+" "+initmipvars_file
    sub.check_call(cmd, shell=True)

    # adjust time axis: shift by two years (PISM issue: wrong time setting), and select
    # the INITMIP 100 yr forcing period,
    cmd = "module load cdo && cdo -O setreftime,20000101,000000,seconds -selyear,2000/2100 -shifttime,-2year "+\
            initmipvars_file+" "+out_file
    sub.check_call(cmd, shell=True)

    print "  Convert added variables to single precision"
    for m_var in pism_copy_vars:

       # ncap2_cmd = 'ncap2 -O -s "{}=float({});time=float(time);time_bounds=float(time_bounds)" '.format(m_var,m_var)
       ncap2_cmd = 'ncap2 -O -s "{}=float({})" '.format(m_var,m_var)
       ncap2_cmd += out_file+' '+out_file
       sub.check_call(ncap2_cmd,shell=True)

       ncatted_cmd = ["ncatted", '-O',
                   "-a", '''_FillValue,{var},o,f,-2e9'''.format(var=m_var),
                   "-a", '''missing_value,{var},o,f,-2e9'''.format(var=m_var),
                   out_file]
       sub.call(ncatted_cmd)

    resources_ismip6.make_scalar_vars_ismip6_conforming(out_file, ismip6_vars_dict)

    # Update attributes
    print('Adjusting attributes')
    nc = CDF(out_file, 'a')
    nc.Conventions = 'CF-1.6'
    nc.institution = 'Potsdam Institute for Climate Impact Research (PIK), Germany'
    nc.contact = 'matthias.mengel@pik-potsdam.de and torsten.albrecht@pik-potsdam.de'
    nc.source = 'PISM; https://github.com/talbrecht/pism_pik; branch: pik/cavity_dev; commit: 8c33b7e8bc1c3cb4e'
    #del nc.variables["pism_config"]
    #del nc.variables["run_stats"]
    #nc.variables["pism_config"] = None
    #nc.variables["run_stats"] = None
    nc.close()

    # remove mask variable
    #cmd = ['ncks', '-O', '-x', '-v', 'pism_config,run_stats',
    #        out_file,
    #        out_file]
    #sub.call(cmd)

    ncatted_cmd = ["ncatted","-hO",
                   "-a", '''nco_openmp_thread_number,global,d,,''',
                   "-a", '''command,global,d,,''',
                   "-a", '''history,global,d,,''',
                   "-a", '''history_of_appended_files,global,d,,''',
                   "-a", '''NCO,global,d,,''',
                   "-a", '''CDI,global,d,,''',
                   "-a", '''_NCProperties,global,d,,''',
                   out_file]
    sub.call(ncatted_cmd)


    print('Finished processing scalar file {}'.format(out_file))

    # if EXP in ('ctrl'):
    #     init_file = '{}/scalar_{}_{}.nc'.format(init_dir, project, 'init')
    #     print('  Copying time 0 to file {}'.format(init_file))
    #     ncks_cmd = ['ncks', '-O', '-4', '-L', '3',
    #                 '-d', 'time,1',
    #                 out_file,
    #                 init_file]
    #     sub.call(ncks_cmd)


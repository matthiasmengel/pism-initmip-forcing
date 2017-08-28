#!/usr/bin/env python
# Copyright (C) 2016 Andy Aschwanden (https://github.com/pism/pism-gris/blob/master/initMIP)
# Modified by Torsten Albrecht for initMIP Antarctica 2017

import os
import glob
import numpy as np
import json
import csv
import cf_units
try:
    import subprocess32 as sub
except:
    import subprocess as sub

from argparse import ArgumentParser
from netCDF4 import Dataset as CDF

#from initMIP.resources_ismip6 import *
import sys
sys.path.append('resources/')
import resources_ismip6; reload(resources_ismip6)

## this hack is needed to import config.py from the project root
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# if project_root not in sys.path: sys.path.append(project_root)
# import config as cf; reload(cf)


working_dir = "/p/tmp/mengel/pism_out/"
experiment = "pismpik_040_initmip08kmforcing_1263d"

experiment_dir = os.path.join(working_dir, experiment)
output_dir = os.path.join(experiment_dir,"postprocessed")

infile = os.path.join(output_dir,"extra_smb_bmelt.nc")


TARGET_GRID_RES_ID = "8"
ID = "1"

IS = 'AIS'
GROUP = 'PIK'
MODEL = 'PISM' + ID + 'EQUI'
EXP = experiment
TYPE = '_'.join([EXP, str(TARGET_GRID_RES_ID).zfill(2)])
INIT = '_'.join(['init', str(TARGET_GRID_RES_ID).zfill(2)])
project = '{IS}_{GROUP}_{MODEL}'.format(IS=IS, GROUP=GROUP, MODEL=MODEL)

pism_stats_vars = ['pism_config',
                   'run_stats']

pism_proj_vars = ['cell_area',
                  'mapping',
                  'lat',
                  'lat_bnds',
                  'lon',
                  'lon_bnds']

mask_var = 'sftgif'


ismip6_vars_dict = resources_ismip6.get_ismip6_vars_dict('ismip6vars.csv', 2)

# ligroundf not available in PISM
ismip6_vars_dict.pop("ligroundf",None)

ismip6_to_pism_dict = dict((k, v.pism_name) for k, v in ismip6_vars_dict.iteritems())
pism_to_ismip6_dict = dict((v.pism_name, k) for k, v in ismip6_vars_dict.iteritems())

pism_copy_vars = [x for x in (ismip6_to_pism_dict.values() + pism_proj_vars)] #+ pism_stats_vars

# base and mapping variable are added later
for var in ["mapping","base"]:
    pism_copy_vars.remove(var)


tmp_file = os.path.join(output_dir, 'tmp.nc')
try:
    os.remove(tmp_file)
except OSError:
    pass

single_variable_dir = os.path.join(output_dir,"single_variables")

if not os.path.exists(single_variable_dir):
    os.makedirs(single_variable_dir)


# Check if request variables are present
nc = CDF(infile, 'r')
for m_var in pism_copy_vars:
    if m_var not in nc.variables:
        print("Requested variable '{}' missing".format(m_var))
nc.close()

print('Extract initmip variables from {} to {}'.format(infile, tmp_file))
cmd = 'ncks -O -4 -L3 -d time,1, -v '+'{}'.format(','.join(pism_copy_vars))+' '+\
       infile+" "+tmp_file
print cmd
sub.check_call(cmd,shell=True)


resources_ismip6.add_base_as_variable(tmp_file)
resources_ismip6.add_projection_info(tmp_file)


# Make the file ISMIP6 conforming
resources_ismip6.make_spatial_vars_ismip6_conforming(tmp_file, ismip6_vars_dict)
ncatted_cmd = ["ncatted",
               "-a", '''bounds,lat,o,c,lat_bnds''',
               "-a", '''bounds,lon,o,c,lon_bnds''',
               "-a", '''coordinates,lat_bnds,d,,''',
               "-a", '''coordinates,lon_bnds,d,,''',
               "-a", '''history,global,d,,''',
               "-a", '''history_of_appended_files,global,d,,''',
               tmp_file]
sub.call(ncatted_cmd)

# Adjust the time axis
# print('Adjusting time axis')

# adjust_time_axis(IS,out_file)

for m_var in ismip6_vars_dict.keys():
    final_file = os.path.join(single_variable_dir, m_var+".nc")
    print('Finalizing variable {}'.format(m_var))
    # Generate file
    print('  Copying to file {}'.format(final_file))
    ncks_cmd = ['ncks', '-O', '-4', '-L', '3',
                '-v', m_var ,
                #'-v', ','.join([m_var,'lat','lon', 'lat_bnds', 'lon_bnds']),
                tmp_file,
                final_file]
    sub.call(ncks_cmd)

    # # set values of grounding line flux to NaN
    # if m_var in ('ligroundf'):
    #   ncap2_cmd = 'ncap2 -O -s "ligroundf = -2e9 * ligroundf ;" '
    #   ncap2_cmd += final_file+' '+final_file
    #   sub.check_call(ncap2_cmd,shell=True)

    if ismip6_vars_dict[m_var].do_mask == 1:

        print('  Mask ice free areas')
        # add mask variable
        cmd = ['ncks', '-A', '-v', '{var}'.format(var=mask_var),
                    tmp_file,
                    final_file]

        sub.call(cmd)
        # mask where mask==0
        cmd = 'ncap2 -O -s "where({maskvar}==0) {var}=-2e9;" '.format(maskvar=mask_var, var=m_var)
        cmd += final_file+' '+final_file
        sub.check_call(cmd,shell=True)


        cmd = ["ncatted", '-O',
               "-a", '''_FillValue,{var},o,f,-2e9'''.format(var=m_var),
               "-a", '''missing_value,{var},o,f,-2e9'''.format(var=m_var),
               final_file]
        sub.call(cmd)

        # remove mask variable
        cmd = ['ncks', '-O', '-x', '-v', '{var}'.format(var=mask_var),
                final_file,
                final_file]
        sub.call(cmd)

    # Update attributes
    print('  Adjusting attributes')

    ncf = CDF(final_file, 'r')
    pism_vars_ff = ncf.variables.keys()
    ncf.close()

    # remove lon lat variable
    var_list='lat_bnds,lon_bnds,lat,lon'
    rm_cmd = ['ncks', '-C','-O', '-x', '-v', '{var}'.format(var=var_list),
              final_file,
              final_file]
    #if all([x in pism_vars_ff for x in var_list]):
    sub.call(rm_cmd)


    float_list=['x', 'y', 'time', 'time_bnds', 'time_bounds']
    #ncap2_cmd = 'ncap2 -O -s "x=float(x);y=float(y);time=float(time);" ' #time_bnds=float(time_bnds);" '
    for var in float_list:
      ncap2_cmd = 'ncap2 -O -s "{}=float({});" '.format(var,var)
      ncap2_cmd += final_file+' '+final_file
      #try:
      if var in pism_vars_ff:
        sub.check_call(ncap2_cmd,shell=True)
      else:
      #except:
        print "  "+var+" is not in final file"

    nc = CDF(final_file, 'a')
    # try:
    nc_var = nc.variables[m_var]
    #nc_var.coordinates = 'lat lon'
    #nc_var.mapping = 'mapping'
    nc_var.standard_name = ismip6_vars_dict[m_var].standard_name
    nc_var.units = ismip6_vars_dict[m_var].units
    nc_var.pism_intent = None
    if ismip6_vars_dict[m_var].state == 1:
        nc_var.cell_methods = 'time: mean (interval: 5 year)'
    # except:
    #     pass

    nc.Conventions = 'CF-1.6'
    nc.institution = 'Potsdam Institute for Climate Impact Research (PIK), Germany'
    nc.contact = 'matthias.mengel@pik-potsdam.de and torsten.albrecht@pik-potsdam.de'
    nc.source = 'PISM; https://github.com/talbrecht/pism_pik; branch: pik/cavity_dev; commit: 8c33b7e8bc1c3cb4e'
    nc.title = 'ISMIP6 AIS InitMIP'
    nc.close()

    ncatted_cmd = ["ncatted","-hO",
               "-a", '''nco_openmp_thread_number,global,d,,''',
               "-a", '''command,global,d,,''',
               "-a", '''history,global,d,,''',
               "-a", '''history_of_appended_files,global,d,,''',
               "-a", '''NCO,global,d,,''',
               "-a", '''CDI,global,d,,''',
               "-a", '''_NCProperties,global,d,,''',
               final_file]
    sub.call(ncatted_cmd)

    print('  Done finalizing variable {}'.format(m_var))

    # if EXP in ('ctrl'):
    #     init_file = '{}/{}_{}_{}.nc'.format(init_dir, m_var, project, 'init')
    #     print('  Copying time 0 to file {}'.format(init_file))
    #     ncks_cmd = ['ncks', '-O', '-4', '-L', '3',
    #                 '-d', 'time,0',
    #                 '-v', m_var,
    #                 final_file,
    #                 init_file]
    #     sub.call(ncks_cmd)

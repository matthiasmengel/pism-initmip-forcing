import os
import numpy as np
import netCDF4 as nc
import shutil
import argparse

# Set up the option parser
parser = argparse.ArgumentParser()
parser.description = "Create initMIP SMB and BMB anomalies for Antarctica."
parser.add_argument("--forcing_file_path", dest="forcing_file_path",
                    help='''Folder for files that will drive PISM''')
parser.add_argument("--background_file", dest="background_file",
                    help='''The reference state we add anomalies to''')
parser.add_argument("--initmip_anomaly_file", dest="initmip_anomaly_file",
                    help='''File with given INITMIP anomalies.''')
options = parser.parse_args()


# pism_input_dir = "/p/projects/pism/mengel/pism_input"
# initmip_anomaly_file = os.path.join(pism_input_dir,"initmip_initmip8km.nc")

make_time_dependent_forcing = True

try:
    nc_initmip = nc.Dataset(options.initmip_anomaly_file,"r")
except IOError as error:
    print options.initmip_anomaly_file, "not present."
    raise error

asmb = nc_initmip.variables["asmb"][:]
abmb = nc_initmip.variables["abmb"][:]

pism_reference_file = nc.Dataset(options.background_file,"r")
smb_background = pism_reference_file.variables['effective_climatic_mass_balance']
temp_background = pism_reference_file.variables['effective_ice_surface_temp']
bmb_background = pism_reference_file.variables['effective_shelf_base_mass_flux']
btemp_background = pism_reference_file.variables['effective_shelf_base_temperature']

startyear = 2000
endyear = 2100
tm = np.arange(startyear,endyear,1.)
years_in_seconds = 60*60*24*365

# from Initmip
ice_density = 910. #kg/m3
# not the same as above:
years_in_second_for_forcing = 31556926.

## from the INITMIP Wiki
# SMB(t) = SMB_initialization + SMB_anomaly * (floor (t) / 40); for 0 < t < 40 in years
# SMB(t) = SMB_initialization + SMB_anomaly * 1.0; for t > 40 years
time_factor = np.ones(100)
time_factor[0:40] = np.linspace(0,1,40)

## Forcing File, having explicit time dimension for climatic_mass_balance, ice_surface_temp
## shelfbmassflux and shelfbtemp
if make_time_dependent_forcing:
    forcing_file = os.path.join(options.forcing_file_path,"initmip_forcing.nc")
    shutil.copyfile(options.initmip_anomaly_file,forcing_file)
    ncf = nc.Dataset(forcing_file,"a")

    ncf.createDimension("time")

    bnds_var_name = "time_bnds"
    bnds_dim = "nb2"
    ncf.createDimension(bnds_dim, 2)

    time_var = ncf.createVariable("time", 'float64', ("time"),)
    time_var.bounds = bnds_var_name
    time_var.units = "seconds since 0000-01-01"
    time_var.calendar = "365_day"
    time_var.axis = 'T'
    time_var[:] = tm*years_in_seconds

    # create time bounds variable
    time_bnds_var = ncf.createVariable(bnds_var_name, 'd', dimensions=("time", bnds_dim))
    time_bnds_var[:, 0] = np.arange(startyear,endyear,1.)*years_in_seconds
    time_bnds_var[:, 1] = np.arange(startyear+1, endyear+1)*years_in_seconds

    climatic_mass_balance = ncf.createVariable("climatic_mass_balance", "float64",("time","y", "x"))
    # convert anomaly from ice equivalent thickness to kg m-2 s-1
    anomaly = (time_factor[:,np.newaxis,np.newaxis] * asmb *
                    ice_density / years_in_second_for_forcing)
    climatic_mass_balance[:] = smb_background[:] + anomaly
    climatic_mass_balance.units = smb_background.units

    # ice_surface_temp does not change from the reference run, just repeated in time
    ice_surface_temp = ncf.createVariable("ice_surface_temp", "float64",("time","y", "x"))
    ice_surface_temp[:] = np.tile(temp_background[:],(len(tm),1,1))
    ice_surface_temp.units = temp_background.units

    shelfbmassflux = ncf.createVariable("shelfbmassflux", "float64",("time","y", "x"))
    # convert anomaly from ice equivalent thickness to kg m-2 year-1 as in pism file.
    anomaly = time_factor[:,np.newaxis,np.newaxis] * abmb * ice_density
    shelfbmassflux[:] = bmb_background[:] + anomaly
    shelfbmassflux.units = bmb_background.units

    # ice_surface_temp does not change from the reference run, just repeated in time
    shelfbtemp = ncf.createVariable("shelfbtemp", "float64",("time","y", "x"))
    shelfbtemp[:] = np.tile(btemp_background[:],(len(tm),1,1))
    shelfbtemp.units = btemp_background.units

    ncf.close()

# Control run file, without explicit time dimension
control_file = os.path.join(options.forcing_file_path,"initmip_control.nc")
shutil.copyfile(options.initmip_anomaly_file,control_file)
ncc = nc.Dataset(control_file,"a")

climatic_mass_balance = ncc.createVariable("climatic_mass_balance", "float64",("y", "x"))
# convert anomaly from ice equivalent thickness to kg m-2 s-1
climatic_mass_balance[:] = smb_background[:]
climatic_mass_balance.units = smb_background.units

ice_surface_temp = ncc.createVariable("ice_surface_temp", "float64",("y", "x"))
ice_surface_temp[:] = temp_background[:]
ice_surface_temp.units = temp_background.units

shelfbmassflux = ncc.createVariable("shelfbmassflux", "float64",("y", "x"))
shelfbmassflux[:] = bmb_background[:]
shelfbmassflux.units = bmb_background.units

# ice_surface_temp does not change from the reference run, just repeated in time
shelfbtemp = ncc.createVariable("shelfbtemp", "float64",("y", "x"))
shelfbtemp[:] = btemp_background[:]
shelfbtemp.units = btemp_background.units

# del ncc.variables["abmb"]

ncc.close()

pism_reference_file.close()
nc_initmip.close()


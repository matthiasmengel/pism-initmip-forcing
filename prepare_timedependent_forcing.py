import os
import numpy as np
import netCDF4 as nc
import shutil

data_dir = "/home/mengel/data/20170822_InitMipAntarctica"
initmip_anomaly_file = os.path.join(data_dir,"initmip_initmip8km.nc")

output_to_input_names = {
 'effective_shelf_base_mass_flux':'shelfbmassflux',
 'effective_shelf_base_temperature':'shelf_base_temperature',
 'effective_climatic_mass_balance':'climatic_mass_balance',
 'effective_ice_surface_temp':'ice_surface_temperature'}

nc_initmip = nc.Dataset(initmip_anomaly_file,"r")
asmb = nc_initmip.variables["asmb"][:]
abmb = nc_initmip.variables["abmb"][:]

pism_reference_file = nc.Dataset(os.path.join(data_dir,"equi_backup.nc"),"r")
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

forcing_file = os.path.join(data_dir,"initmip_forcing.nc")
shutil.copyfile(initmip_anomaly_file,forcing_file)
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
climatic_mass_balance[:] = smb_background + anomaly
climatic_mass_balance.units = smb_background.units

# ice_surface_temp does not change from the reference run, just repeated in time
ice_surface_temp = ncf.createVariable("ice_surface_temp", "float64",("time","y", "x"))
ice_surface_temp[:] = np.tile(temp_background,(len(tm),1,1))
ice_surface_temp.units = temp_background.units



shelfbmassflux = ncf.createVariable("shelfbmassflux", "float64",("time","y", "x"))
# convert anomaly from ice equivalent thickness to kg m-2 year-1 as in pism file.
anomaly = time_factor[:,np.newaxis,np.newaxis] * abmb * ice_density
shelfbmassflux[:] = bmb_background + anomaly
shelfbmassflux.units = bmb_background.units

# ice_surface_temp does not change from the reference run, just repeated in time
shelfbtemp = ncf.createVariable("shelfbtemp", "float64",("time","y", "x"))
shelfbtemp[:] = np.tile(btemp_background,(len(tm),1,1))
shelfbtemp.units = btemp_background.units

pism_reference_file.close()
nc_initmip.close()
ncf.close()
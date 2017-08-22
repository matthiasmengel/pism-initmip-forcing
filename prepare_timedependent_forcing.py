import numpy as np
import netCDF4 as nc
import shutil

anomaly_file = "/p/projects/pism/mengel/pism_input/initmip/initmip_initmip8km.nc"

ncin = nc.Dataset(anomaly_file,"r")
asmb = ncin.variables["asmb"][:]
abmb = ncin.variables["abmb"][:]

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

tforce_file = "/p/projects/pism/mengel/pism_input/initmip/tforce_8km.nc"
shutil.copyfile(anomaly_file,tforce_file)
ncf = nc.Dataset(tforce_file,"a")

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

asmb_t = ncf.createVariable("climatic_mass_balance_anomaly", "float64",("time","y", "x"))
asmb_t[:] = time_factor[:,np.newaxis,np.newaxis] * asmb * \
                ice_density / years_in_second_for_forcing
asmb_t.units = "kg m-2 s-1"

# this anomaly is set to zero, we put here as pism needs it.
atemp_t = ncf.createVariable("ice_surface_temp_anomaly", "float64",("time","y", "x"))
atemp_t[:] = np.zeros([len(tm),ncf.variables["y"].shape[0],
                        ncf.variables["x"].shape[0]]) + 273.15
atemp_t.units = "Kelvin"

ncin.close()
ncf.close()
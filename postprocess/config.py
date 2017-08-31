

working_dir = "/p/tmp/mengel/pism_out/"
experiment = "pismpik_040_initmip08kmforcing_1263i"

project = 'AIS_PIK_PISM4EQUI'
resolution = "8"

initmip_naming = {"smb_bmelt":"asmb_abmb","smb":"asmb","bmelt":"abmb","ctrl":"ctrl"}
ts_naming = {"smb_bmelt":"","smb":"_smb","bmelt":"_bmelt","ctrl":"_ctrl"}


# pism_stats_vars = ['pism_config',
#                    'run_stats']

pism_proj_vars = ['cell_area',
                  'mapping',
                  'lat',
                  'lat_bnds',
                  'lon',
                  'lon_bnds']

mask_var = 'sftgif'
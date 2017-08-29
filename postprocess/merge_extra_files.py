
import os
import glob
import subprocess

working_dir = "/p/tmp/mengel/pism_out/"
experiment = "pismpik_040_initmip08kmforcing_1263d"

experiment_dir = os.path.join(working_dir, experiment)
output_dir = os.path.join(experiment_dir,"postprocessed")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

mergefile = {"_":"smb_bmelt","_smb_":"smb","_bmelt_":"bmelt","_ctrl_":"ctrl"}

for exp in ["_","_smb_","_bmelt_","_ctrl_"]:

    files_to_merge = sorted(glob.glob(experiment_dir+"/extra"+exp+"[1-2]*.000.nc"))
    merged_file = os.path.join(output_dir,"extra_"+mergefile[exp]+".nc")

    cmd = "cdo -O -f nc4c -v mergetime "+" ".join(files_to_merge)+" "+merged_file
    print cmd
    subprocess.check_call(cmd,shell=True)
    #add x and y and mapping
    cmd = 'ncks -A -v x,y '+files_to_merge[0]+" "+merged_file
    subprocess.check_call(cmd, shell=True)

    print merged_file, "merged."
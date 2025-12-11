## Use conda env "brsdk" ##
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from brainrender.scene import Scene
from brainrender.actors import Line, Point, Points, ruler
from brainrender import settings


#### Set plotting parameters ####
probes_csv_file = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\CL-CM stim\CLstimpilot_03192025_probescoords.csv") # set the directory where 'mouseXXXXXX' folders exist
save_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\CL-CM stim")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
target_region = 'CL'

## Set brainrender settings ##
settings.SHOW_AXES = False

## Create the scene with correct atlas ##
scene = Scene(
    atlas_name="allen_mouse_25um", inset=False,
    title='test', screenshots_folder=save_dir,
)
MLdist = scene.atlas.annotation.shape[-1]

## Add target brain region ##
CL = scene.add_brain_region(target_region, alpha=0.8, color='coral', hemisphere='left')
CLcom = CL.center_of_mass()
## Set target in left CL ##
leftCL_CCF = np.array([270, 140, 194])
leftCL_CCF[-1] = MLdist - leftCL_CCF[-1] # mirror ML
leftCL_brcoords = leftCL_CCF * pixel_scale # plot um in brainrender space

## Get a region ##
all_probes_df = pd.read_csv(probes_csv_file)
stim_tips = all_probes_df[all_probes_df['probe'] == 'stim_neg'].reset_index(drop=True)

## Test on one session ##
# ii = 7
# stimrow = stim_tips.iloc[ii]
# tipcoords = np.array([stimrow.tipAP, stimrow.tipDV, stimrow.tipML])
# tipcoords[-1] = MLdist - tipcoords[-1] # mirror ML
# BR_coords = tipcoords * pixel_scale # plot um in brainrender space
# ## distii = np.linalg.norm(BR_coords - CLcom) # dist from CL center of mass
# distii = np.linalg.norm(BR_coords - leftCL_brcoords)
# print(distii * 1E-3)

## Loop through all sessions ##
dist_list = []
for ii, stimrow in stim_tips.iterrows():
    tipcoords = np.array([stimrow.tipAP, stimrow.tipDV, stimrow.tipML])
    tipcoords[-1] = MLdist - tipcoords[-1] # mirror ML
    BR_coords = tipcoords * pixel_scale # plot um in brainrender space
    # dist_list.append(np.linalg.norm(BR_coords - CLcom) * 1E-3)
    dist_list.append(np.linalg.norm(BR_coords - leftCL_brcoords) * 1E-3)

stim_tips['dist_CL'] = dist_list
print(stim_tips)
stim_tips.to_csv(os.path.join(save_dir, 'all_subs_stimdist.csv'), index=False)

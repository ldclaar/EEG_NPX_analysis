## Use conda env "brsdk" ##
import json
import os
import sys
from pathlib import Path

import gspread
import numpy as np
import pandas as pd

from brainrender.scene import Scene
from brainrender.actors import Line, Points
from brainrender import settings
sys.path.append(r'C:\Users\lesliec\code')
from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp

#### Set plotting parameters ####
subexpind = 84 # index of the example subject from the Templeton log
data_dir = Path("F:\psi_exp") # set the directory where 'mouseXXXXXX' folders exist
# units_csv_file = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\brainrender_test_mouse735049_units_info.csv") # set the directory where 'mouseXXXXXX' folders exist
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\plots\brainrender_figs")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"br_probes_test2"
show_regions = True
regions = ['AV', 'CL', 'MD', 'PO', 'PF', 'VAL', 'VPL', 'VPM', 'VM']

## Set brainrender settings ##
settings.SHOW_AXES = False

## Load the Templeton log sheet as pd.DataFrame ##
_gc = gspread.service_account() # need a key file to access the account
_sh = _gc.open('Templeton-log_exp') # open the spreadsheet
_df = pd.DataFrame(_sh.sheet1.get()) # load the first worksheet
metadata = _df.T.set_index(0).T # put it in a nicely formatted dataframe

## Select subject/experiment ##
expmeta = metadata.iloc[subexpind]
print('{}: {}'.format(expmeta['mouse_name'], expmeta['exp_name']))
dataloc = os.path.join(
    data_dir, expmeta['mouse_name'], expmeta['exp_name'], 'experiment1', 'recording1'
)
exp = EEGexp(dataloc, preprocess=False, make_stim_csv=False)
probe_list = [x.replace('_sorted', '') for x in exp.experiment_data if 'probe' in x]

## Get probe coordinates ##
probe_CCF_coords = {}
for probei in probe_list:
    print(' {}'.format(probei))
    with open(exp.ephys_params[probei]['probe_info']) as data_file:
        data = json.load(data_file)
    if 'ccf_coord_ch' in data.keys():
        ch_coords = np.array(data['ccf_coord_ch'])
        ccf_res = data['ccf_resolution']
        probe_CCF_coords[probei] = np.array([ch_coords[0], ch_coords[-1]]) # for a Line
        # probe_CCF_coords[probei] = ch_coords # for Points
    else:
        print('  No locations for this probe.')


## Create the scene with correct atlas ##
scene = Scene(
    atlas_name="allen_mouse_25um", inset=False,
    title='test plot: all probes from 735049',
    screenshots_folder=plot_dir,
)

## Add brain regions ##
# Scene.add_brain_region(regions, alpha, color, silhouette, hemisphere, force)
if show_regions:
    for regi in regions:
        scene.add_brain_region(regi, alpha=0.1, hemisphere='left')

## Convert from CCF coords to brainrender coords ##
MLdist = scene.atlas.annotation.shape[-1]

########################################################
## Create Line actors for each probe and add to Scene ##
for probei, coords in probe_CCF_coords.items():
    coords[:,-1] = MLdist - coords[:,-1] # mirror ML
    BR_coords = coords * pixel_scale # plot um in brainrender space
    scene.add(Line(BR_coords, color='k', linewidth=10, name=probei))

## Create Points actors for each probe and add to Scene ##
# for probei, coords in probe_CCF_coords.items():
#     coords[:,-1] = MLdist - coords[:,-1] # mirror ML
#     BR_coords = coords * pixel_scale # plot um in brainrender space
#     scene.add(Points(BR_coords, colors='k', radius=20))
########################################################

## Slice the brain ##
# scene.slice("sagittal") # this slices correctly, but shows the right hemisphere only
scene.slice("sagittal", invert=True) # this slices correctly!

## Display the figure. ##
scene.render(interactive=True, camera='sagittal')
# camera options: 'top'
# interactive=False to save a screenshot
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
# scene.screenshot(name=screenshot_name, scale=3)
# scene.close()

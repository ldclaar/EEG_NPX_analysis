## Use conda env "brsdk" ##
import json
import os
import sys
from pathlib import Path

import gspread
import numpy as np
import pandas as pd

from brainrender.scene import Scene
from brainrender.actors import Points
from brainrender import settings
# from vedo import shapes
sys.path.append(r'C:\Users\lesliec\code')
from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp

#### Set plotting parameters ####
subexpind = 84 # index of the example subject from the Templeton log
data_dir = Path("F:\psi_exp") # set the directory where 'mouseXXXXXX' folders exist
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\plots\brainrender_figs")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords


## Set brainrender settings ##
settings.SHOW_AXES = False

## Load the Templeton log sheet as pd.DataFrame ##
_gc = gspread.service_account() # need a key file to access the account
_sh = _gc.open('Templeton-log_exp') # open the spreadsheet
_df = pd.DataFrame(_sh.sheet1.get()) # load the first worksheet
metadata = _df.T.set_index(0).T # put it in a nicely formatted dataframe


expmeta = metadata.iloc[subexpind]

print('{}: {}'.format(expmeta['mouse_name'], expmeta['exp_name']))
dataloc = os.path.join(
    data_dir, expmeta['mouse_name'], expmeta['exp_name'], 'experiment1', 'recording1'
)

exp = EEGexp(dataloc, preprocess=False, make_stim_csv=False)
probe_list = [x.replace('_sorted', '') for x in exp.experiment_data if 'probe' in x]

all_units_list = []
for probei in probe_list:
    print(' {}'.format(probei))
    select_units, peak_chs, unit_metrics = exp.get_probe_units(probei)
    unit_metrics['unit_name'] = [probei[-1] + str(x) for x in unit_metrics['cluster_id'].values]
    all_units_list.append(unit_metrics)
all_select_units = pd.concat(all_units_list)

all_CCF_coords = []
for ui, urow in all_select_units.iterrows():
    all_CCF_coords.append(
        [int(x) for x in urow['ccf_coord'].replace('[','').replace(']','').replace(' ','').split(',')]
    )
all_CCF_coords = np.array(all_CCF_coords)

## Create the scene with correct atlas ##
scene = Scene(
    atlas_name="allen_mouse_25um", inset=False,
    title='{}: {}'.format(expmeta['mouse_name'], expmeta['exp_name']),
    screenshots_folder=plot_dir,
)

## Convert from CCF coords to brainrender coords ##
MLdist = scene.atlas.annotation.shape[-1]
all_CCF_coords[:,-1] = MLdist - all_CCF_coords[:,-1] # mirror ML
all_BR_coords = all_CCF_coords * pixel_scale # plot um in brainrender space

## Create a Points actor for the units ##
units = Points(all_BR_coords, colors='OliveDrab', radius=60, alpha=0.5)
## Add to scene ##
scene.add(units)

## Slice the brain ##
# scene.slice("sagittal") # this slices correctly, but shows the right hemisphere only
plane = scene.atlas.get_plane(norm=(0, 1, -1))
scene.slice(plane)

## Display the figure. ##
scene.render()
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
# scene.screenshot(name=r'EEG_chs_crans', scale=3)
# scene.close()

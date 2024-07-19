## Use conda env "brsdk" ##
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from brainrender.scene import Scene
from brainrender.actors import Line, Points
from brainrender import settings


#### Set plotting parameters ####
probes_csv_file = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\HMpaper_SR_07182024_probescoords.csv") # set the directory where 'mouseXXXXXX' folders exist
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\plots\brainrender_figs")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"HMpaper_SR_07182024_sag_probes"
show_regions = True
regions = ['AV', 'CL', 'MD', 'PO', 'PF', 'VAL', 'VPL', 'VPM', 'VM']
br_title = 'HMpaper_SR_07182024: SM-TH probes'

region_colors = {
    'AV': 'HotPink',
    'CL': 'Red',
    'MD': 'Orange',
    'PO': 'Gold',
    'PF': 'Sienna',
    'VAL': 'Purple',
    'VPL': 'Blue',
    'VPM': 'Cyan',
    'VM': 'Green',
}

## Set brainrender settings ##
settings.SHOW_AXES = False

## Create the scene with correct atlas ##
scene = Scene(
    atlas_name="allen_mouse_25um", inset=False,
    title=br_title, screenshots_folder=plot_dir,
)
MLdist = scene.atlas.annotation.shape[-1]

## Add brain regions ##
# Scene.add_brain_region(regions, alpha, color, silhouette, hemisphere, force)
if show_regions:
    for regi in regions:
        scene.add_brain_region(
            regi, alpha=0.2, color=region_colors[regi], hemisphere='left'
        )

## Load multi-probes csv ##
all_probes_df = pd.read_csv(probes_csv_file)
## Create Line actors for each probe and add to Scene ##
for indi, probe_info in all_probes_df.iterrows():
    coords = np.array([
        [probe_info.tipAP, probe_info.tipDV, probe_info.tipML],
        [probe_info.surfAP, probe_info.surfDV, probe_info.surfML]
    ])
    coords[:,-1] = MLdist - coords[:,-1] # mirror ML
    BR_coords = coords * pixel_scale # plot um in brainrender space
    scene.add(Line(BR_coords, color='k', alpha=0.9, linewidth=4, name=probe_info.probe))

## Slice the brain ##
# scene.slice("sagittal") # this slices correctly, but shows the right hemisphere only
scene.slice("sagittal", invert=True) # this slices correctly!

## Display the figure. ##
scene.render(interactive=False, camera='sagittal', zoom=2)
# camera options: 'top'
# interactive=False to save a screenshot
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
scene.screenshot(name=screenshot_name, scale=3)
scene.close()

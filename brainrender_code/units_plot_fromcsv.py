## Use conda env "brsdk" ##
import json
import os
import sys
from pathlib import Path

import gspread
import numpy as np
import pandas as pd

from brainrender.scene import Scene
from brainrender.actors import Point, Points
from brainrender import settings


#### Set plotting parameters ####
units_csv_file = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\HMpaper_SR_07182024_unitscoords.csv") # set the directory where 'mouseXXXXXX' folders exist
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\plots\brainrender_figs")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"HMpaper_SR_07182024_sag_units"
show_regions = True
regions = ['AV', 'CL', 'MD', 'PO', 'PF', 'VAL', 'VPL', 'VPM', 'VM']
br_title = 'HMpaper_SR_07182024: TH units'
show_legend = True

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
            regi, alpha=0.1, color=region_colors[regi], hemisphere='left'
        )
## Add legend circles ##
if show_legend:
    for ii, (regi, rcol) in enumerate(region_colors.items()):
        temp = scene.add(Point((4000, 3000 + (ii * 150), 7000), radius=50, color=rcol))
        # scene.add_label(temp, regi)
    temp = scene.add(Point((4000, 3000 + ((ii+1) * 150), 7000), radius=50, color='Gray'))

## Load unit csv ##
all_units_df = pd.read_csv(units_csv_file) #.astype({'parameter': int})

## Convert from CCF coords to brainrender coords ##
all_CCF_coords = np.array(
    [all_units_df.CCF_AP.values, all_units_df.CCF_DV.values, all_units_df.CCF_ML.values]
).T
all_CCF_coords[:,-1] = MLdist - all_CCF_coords[:,-1] # mirror ML
all_BR_coords = all_CCF_coords * pixel_scale # plot um in brainrender space

## Create a Points actor for the units ##
if 'color' in all_units_df.columns:
    units = Points(all_BR_coords, colors=all_units_df.color.values, radius=40, alpha=0.3)
else:
    units = Points(all_BR_coords, radius=40, alpha=0.3)

## Add to scene ##
scene.add(units)

## Slice the brain ##
scene.slice("sagittal", invert=True) # this slices correctly!
# scene.slice("sagittal") # this slices correctly, but shows the right hemisphere only
# plane = scene.atlas.get_plane(norm=(0, 1, -1))
# scene.slice(plane)

## Display the figure. ##
scene.render(interactive=False, camera='sagittal', zoom=4)
# camera options: 'top'
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
scene.screenshot(name=screenshot_name, scale=3)
scene.close()

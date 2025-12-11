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
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\pictures")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"striatum"
show_regions = True
plot_regions = ['CP', 'ACB', 'OT'] #, 'CP', 'AV', 'HIP']
br_title = 'striatum'
show_legend = False
show_scalebar = False

region_colors = {
    'CP': 'Blue',
    'ACB': 'Purple',
    'OT': 'Orange',
    # 'MD': 'Orange',
    # 'PO': 'Gold',
    # 'RT': 'Sienna',
    # 'VAL': 'Purple',
    # 'VPL': 'Blue',
    # 'VPM': 'Cyan',
    # 'VM': 'Green',
    # 'TH': 'Gray',
    # 'CP': 'Gray',
    # 'HIP': 'Gray',
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
    # for regi in target_regions:
    #     CL = scene.add_brain_region(regi, alpha=0.8, color=region_colors[regi])#, hemisphere='left')
    for regi in plot_regions:
        scene.add_brain_region(regi, alpha=0.5, color=region_colors[regi])#, hemisphere='left')
## Add legend circles ##
if show_legend:
    for ii, (regi, rcol) in enumerate(region_colors.items()):
        temp = scene.add(Point((4000, 3000 + (ii * 150), 7000), radius=50, color=rcol))
        # scene.add_label(temp, regi)
    # temp = scene.add(Point((4000, 3000 + ((ii+1) * 150), 7000), radius=50, color='Gray'))
## Add scale bar ##
if show_scalebar:
    scene.add(Line(np.array([[5000,5000,6000], [4000,5000,6000]]), color='k', linewidth=5, name='scale bar'))
    # The scale bar is 1 mm, original units are um ##
    # scene.add(ruler(np.array([5000,5000,6000]), np.array([4000,5000,6000]), unit_scale=0.001, units="mm"))

## Add scale bar for top view ##
# right side, near CL: np.array([[6500,3000,4000], [7500,3000,4000]]
# left side, ant to CL: np.array([[5000,1000,8500], [6000,1000,8500]]
# scene.add(Line(np.array([[5000,1000,8500], [6000,1000,8500]]), color='k', linewidth=8, name='scale bar'))

## Add scale bar for frontal view ##
# right side, near CL: np.array([[6500,3000,4000], [7500,3000,4000]]
# left side, ant to CL: np.array([[5000,1000,8500], [6000,1000,8500]]
scene.add(Line(np.array([[7000,6000,8000], [8000,6000,8000]]), color='k', linewidth=8, name='scale bar'))


## Slice the brain ##
# scene.slice("frontal", invert=True)
scene.slice("sagittal", invert=True) # this slices correctly!

## Display the figure. ##
## Custom camera ##
# custom_camera = {
#     "pos": (27500, -1428, -5763),
#     "viewup": (0, -1, 0),
#     "clipping_range": (31983, 76783),
# }
# custom_camera = {
#     "pos": (-19199, -1428, -5763),
#     "viewup": (0, -1, 0),
#     "clipping_range": (19531, 40903),
# }
scene.render(interactive=False, camera='sagittal', zoom=1)
# camera options: 'top', 'sagittal', 'three_quarters'
# interactive=False to save a screenshot
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
## scale changes the resolution, > 1 for higher res
# scene.render(interactive=False, camera='top', zoom=1)
scene.screenshot(name=screenshot_name, scale=2)
scene.close()

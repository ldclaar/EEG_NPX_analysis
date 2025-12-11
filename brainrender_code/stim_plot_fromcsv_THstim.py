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
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\CL-CM stim\pictures and plots")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"THstimpilot_allstimlocs_sag_legend"
show_regions = True
target_regions = ['CL', 'CM']
other_regions = ['TH'] #, 'CP', 'AV', 'HIP']
br_title = 'CL/CM stim: stim locations'
show_legend = False
show_scalebar = False
show_probes = False
show_stim = True
show_stim_legend = True

region_colors = {
    'CL': 'Red',
    'CM': 'Purple',
    'AV': 'HotPink',
    'MD': 'Orange',
    'PO': 'Gold',
    'RT': 'Sienna',
    'VAL': 'Purple',
    'VPL': 'Blue',
    'VPM': 'Cyan',
    'VM': 'Green',
    'TH': 'Gray',
    'CP': 'Gray',
    'HIP': 'Gray',
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
    for regi in target_regions:
        scene.add_brain_region(
            regi, alpha=0.5, color=region_colors[regi], hemisphere='left'
        )
    for regi in other_regions:
        scene.add_brain_region(
            regi, alpha=0.1, color=region_colors[regi], hemisphere='left'
        )
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

## Load multi-probes csv ##
if show_probes:
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
        scene.add(Point(BR_coords[0], radius=40, color='k', alpha=0.9))
    # scene.add(ruler(BR_coords[0], BR_coords[1], unit_scale=0.001, units="mm")) # confirms unit scale

## Add stim tips circles ##
if show_stim:
    all_probes_df = pd.read_csv(probes_csv_file)
    ii = 0
    for indi, probe_info in all_probes_df.iterrows():
        if 'probe' in probe_info.probe:
            continue
        coords = np.array([
            [probe_info.tipAP, probe_info.tipDV, probe_info.tipML],
            [probe_info.surfAP, probe_info.surfDV, probe_info.surfML]
        ])
        coords[:,-1] = MLdist - coords[:,-1] # mirror ML
        BR_coords = coords * pixel_scale # plot um in brainrender space
        if 'neg' in probe_info.probe:
            scene.add(Line(BR_coords, color=probe_info.color, alpha=0.8, linewidth=7, name=probe_info.probe))
            scene.add(Point(BR_coords[0,:], radius=40, color='r'))
            if show_stim_legend:
                stname = probe_info.mouse[-6:] + '-day' + probe_info.experiment[8] + ': ' + probe_info.tiparea
                legendcoords = [[4800, 3000 + (ii * 250), 6000], [5100, 3000 + (ii * 250), 6000]]
                temp = scene.add(Line(legendcoords, color=probe_info.color, alpha=0.8, linewidth=7, name=stname))
                label_args = {'size': 150, 'radius': None, 'yoffset': 340, 'zoffset': -340}
                scene.add_label(temp, stname, **label_args)
                ii += 1
        if 'pos' in probe_info.probe:
            scene.add(Point(BR_coords[0,:], radius=35, color='b'))

## Slice the brain ##
# scene.slice("sagittal") # this slices correctly, but shows the right hemisphere only
scene.slice("sagittal", invert=True) # this slices correctly!

## Display the figure. ##
scene.render(interactive=False, camera='sagittal', zoom=1.9)
# camera options: 'top', 'sagittal', 'three_quarters'
# interactive=False to save a screenshot
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
scene.screenshot(name=screenshot_name, scale=3)
scene.close()

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
subs_csv_file = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\THStim_allsubjects.csv") # set the directory where 'mouseXXXXXX' folders exist
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\plots\brainrender_figs")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"THstim_01142025_stimlocs_top"
show_regions = True
regions = ['CL', 'CM']
br_title = 'CL/CM stim: stim locations'
show_legend = False
show_scalebar = False
show_probes = False
show_stim = True

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
            regi, alpha=0.25, color=region_colors[regi], hemisphere='left'
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
    all_subjects_df = pd.read_csv(subs_csv_file)
    for indi, sub_info in all_subjects_df.iterrows():
        tip_coords = np.array([sub_info.stim_tip_AP, sub_info.stim_tip_DV, sub_info.stim_tip_ML])
        # surf_coords = np.array([sub_info.stim_surf_AP, sub_info.stim_surf_DV, sub_info.stim_surf_ML])
        ## Calculate the supposed position of the 2nd tip ##
        # stim_elec_vec = tip_coords - surf_coords
        # norm = np.linalg.norm(stim_elec_vec)
        # direction = stim_elec_vec / norm # unit vector
        # other_tip_coords = (tip_coords - (0.3/0.025) * direction).astype(int)
        ## transform and plot them ##
        tip_coords[-1] = MLdist - tip_coords[-1] # mirror ML
        T1_coords = tip_coords * pixel_scale # plot um in brainrender space
        scene.add(Point(T1_coords, radius=50, color=str(sub_info.color)))
        # scene.add(Point(T1_coords, radius=50, color='b'))

        # other_tip_coords[:,-1] = MLdist - other_tip_coords[:,-1] # mirror ML
        # T2_coords = other_tip_coords * pixel_scale # plot um in brainrender space
        # scene.add(Point(T2_coords, radius=50, color='b'))


## Slice the brain ##
# scene.slice("sagittal") # this slices correctly, but shows the right hemisphere only
scene.slice("sagittal", invert=True) # this slices correctly!

## Display the figure. ##
scene.render(interactive=False, camera='top', zoom=2)
# camera options: 'top', 'sagittal'
# interactive=False to save a screenshot
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
scene.screenshot(name=screenshot_name, scale=3)
scene.close()

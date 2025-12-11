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
subject_csv_file = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\CL-CM stim\subject_metadata.csv")
probes_csv_file = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\CL-CM stim\CLstimpilot_03122025_probescoords.csv")
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\CL-CM stim\pictures and plots")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"CLstimpilot_03122025_probes_top"
show_regions = True
br_title = 'CL stim experiments: all probes (03/2025)'
show_legend = False
show_scalebar = False
show_stim = True

region_colors = {
    'CL': 'darkgreen',
    'CM': 'orange',
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
    for regi, regcol in region_colors.items():
        scene.add_brain_region(
            regi, alpha=0.25, color=regcol, hemisphere='left'
        )
## Add legend circles ##
if show_legend:
    for ii, (regi, rcol) in enumerate(region_colors.items()):
        temp = scene.add(Point((4000, 3000 + (ii * 150), 7000), radius=50, color=rcol))
        # scene.add_label(temp, regi)
    # temp = scene.add(Point((4000, 3000 + ((ii+1) * 150), 7000), radius=50, color='Gray'))
## Add scale bar ##
if show_scalebar:
    scene.add(Line(np.array([[4000,5500,7000], [3000,5500,7000]]), color='k', linewidth=5, name='scale bar'))
    # The scale bar is 1 mm, original units are um ##
    # scene.add(ruler(np.array([5000,5000,6000]), np.array([4000,5000,6000]), unit_scale=0.001, units="mm"))

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
    if probe_info.close_to_stim:
        prcol = 'k'
    else:
        prcol = 'r'
    scene.add(Line(BR_coords, color=prcol, alpha=0.9, linewidth=4, name=probe_info.probe))
    # scene.add(Point(BR_coords[0], radius=40, color='k', alpha=0.9)) # adds a sphere to the end of the probe-CK
# scene.add(ruler(BR_coords[0], BR_coords[1], unit_scale=0.001, units="mm")) # confirms unit scale

## Add stim tips circles ##
if show_stim:
    all_subjects_df = pd.read_csv(subject_csv_file)
    for indi, sub_info in all_subjects_df.iterrows():
        tip_coords = np.array([sub_info.stim_tip_AP, sub_info.stim_tip_DV, sub_info.stim_tip_ML])
        surf_coords = np.array([sub_info.stim_surf_AP, sub_info.stim_surf_DV, sub_info.stim_surf_ML])
        ## Calculate the supposed position of the 2nd tip ##
        stim_elec_vec = tip_coords - surf_coords
        norm = np.linalg.norm(stim_elec_vec)
        direction = stim_elec_vec / norm # unit vector
        other_tip_coords = (tip_coords - (0.3/0.025) * direction).astype(int)
        ## transform and plot them ##
        tip_coords[:,-1] = MLdist - tip_coords[:,-1] # mirror ML
        T1_coords = tip_coords * pixel_scale # plot um in brainrender space
        scene.add(Point(T1_coords, radius=50, color='b'))

        other_tip_coords[:,-1] = MLdist - other_tip_coords[:,-1] # mirror ML
        T2_coords = other_tip_coords * pixel_scale # plot um in brainrender space
        scene.add(Point(T2_coords, radius=50, color='b'))

## Slice the brain ##
# scene.slice("sagittal") # this slices correctly, but shows the right hemisphere only
# scene.slice("sagittal", invert=True) # this slices correctly!

## Custom camera view ##
# ccamera = {
#     "pos": (1000, 1000, 0), # (8777, 1878, -44032),
#     "viewup": (0, -1, 0),
#     "clipping_range": (24852, 54844),
#     "focal_point": (7718, 4290, -3507),
#     "distance": 40610,
# }

## Display the figure. ##
# scene.render(interactive=False, camera='sagittal', zoom=2)
scene.render(interactive=False, camera='top', zoom=1)
# scene.render(interactive=True, camera=ccamera, zoom=1.2)
# camera options: 'top'
# interactive=False to save a screenshot
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
scene.screenshot(name=screenshot_name, scale=3)
scene.close()

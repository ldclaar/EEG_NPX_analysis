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
EEG_info_csv_path = Path(
    r"C:\Users\lesliec\OneDrive - Allen Institute\analysis\GAT1-KO_analyses\brainrender\EEG_electrodes_info.csv"
)
subject_csv_file = Path(
    r"C:\Users\lesliec\OneDrive - Allen Institute\analysis\GAT1-KO_analyses\brainrender\GAT1_NPephys_subjects_brainrender.csv"
)
probes_csv_file = Path(
    r"C:\Users\lesliec\OneDrive - Allen Institute\analysis\GAT1-KO_analyses\brainrender\SLC6A1-KO_08292025_probescoords.csv"
)
plot_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\analysis\GAT1-KO_analyses\brainrender")
pixel_scale = 25 # scale from 25 um CCF to brainrender coords
screenshot_name = r"SLC6A1subs_10222025_EEGNPX"
show_regions = True
target_regions = []
other_regions = ['TH', 'STR', 'HIP', 'MO', 'SS', 'VIS'] # 'Isocortex'
br_title = 'All SLC6A1-KO experiments: all probes (10/2025)'
show_legend = False
show_scalebar = False
show_stim = True
plot_one_subject = 672785 # enter one subject or None
show_elecs = True # True/False to show the EEG electrodes as circles on the brain
show_screws = True # True/False to show the gnd/ref screws as circles over the cb
elec_color = 'k'
elec_radius = 250 # these are roughly um, electrodes are 500 um in diameter

region_colors = {
    'TH': 'Gray',
    'STR': 'red',
    'HIP': 'purple',
    'OLF': 'orange',
    'Isocortex': 'mediumseagreen',
    'MO': 'mediumseagreen',
    'SS': 'seagreen',
    'VIS': 'teal',
}

# if plot_one_subject is not None:
#     screenshot_name = 'CLstimpilot_' + plot_one_subject + '_allsessions'
#     br_title = 'CL stim: ' + plot_one_subject + ', all sessions'

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
            regi, alpha=0.5, color=region_colors[regi], # hemisphere='left'
        )
    for regi in other_regions:
        scene.add_brain_region(
            regi, alpha=0.2, color=region_colors[regi], silhouette=False, # hemisphere='left'
        )
## Add legend circles ##
if show_legend:
    for ii, (regi, rcol) in enumerate(region_colors.items()):
        temp = scene.add(Point((4000, 3000 + (ii * 150), 7000), radius=50, color=rcol))
        # scene.add_label(temp, regi)
    # temp = scene.add(Point((4000, 3000 + ((ii+1) * 150), 7000), radius=50, color='Gray'))
## Add scale bar ##
if show_scalebar:
    scene.add(Line(np.array([[3000,5500,6000], [2000,5500,6000]]), color='k', linewidth=5, name='scale bar'))
    # The scale bar is 1 mm, original units are um ##
    # scene.add(ruler(np.array([5000,5000,6000]), np.array([4000,5000,6000]), unit_scale=0.001, units="mm"))

#### Load EEG information ####
EEG_ch_info = pd.read_csv(EEG_info_csv_path)
## Add electrodes ##
if show_elecs:
    for indi, chi_info in EEG_ch_info.iterrows():
        elec_coords = np.array([chi_info.x, chi_info.y, chi_info.z]) * pixel_scale
        elec_coords[1] -= 200
        scene.add(Point(elec_coords, color=elec_color, radius=elec_radius))
## Add skull screws ##
if show_screws: # SLC6A1 mice had only 2 skull screws
    screw_coords = np.array([
        [11000, 1000, 7500],
        [11000, 1000, 3900]
    ])
    for coordi in screw_coords:
        scene.add(Point(coordi, color='dimgray', radius=300))

#### Load multi-probes csv ####
all_probes_df = pd.read_csv(probes_csv_file)

## Choose one subject, if listed ##
if plot_one_subject is not None:
    choose_df = all_probes_df[all_probes_df['mouse'] == plot_one_subject]
else:
    choose_df = all_probes_df

## Create Line actors for each probe and add to Scene ##
for indi, probe_info in choose_df.iterrows():
    if 'probe' not in probe_info.probe:
        continue
    coords = np.array([
        [probe_info.tipAP, probe_info.tipDV, probe_info.tipML],
        [probe_info.surfAP, probe_info.surfDV, probe_info.surfML]
    ])
    coords[:,-1] = MLdist - coords[:,-1] # mirror ML
    BR_coords = coords * pixel_scale # plot um in brainrender space
    scene.add(Line(BR_coords, color='k', alpha=0.9, linewidth=6, name=probe_info.probe))
    # scene.add(Line(BR_coords, color=probe_info.color, alpha=0.9, linewidth=7, name=probe_info.probe))

# scene.add(ruler(BR_coords[0], BR_coords[1], unit_scale=0.001, units="mm")) # confirms unit scale

## Add stim tips circles ##
if show_stim:
    for indi, probe_info in choose_df.iterrows():
        if 'probe' in probe_info.probe:
            continue
        coords = np.array([
            [probe_info.tipAP, probe_info.tipDV, probe_info.tipML],
            [probe_info.surfAP, probe_info.surfDV, probe_info.surfML]
        ])
        coords[:,-1] = MLdist - coords[:,-1] # mirror ML
        BR_coords = coords * pixel_scale # plot um in brainrender space
        if 'neg' in probe_info.probe:
            scene.add(Line(BR_coords, color='gray', alpha=0.9, linewidth=6, name=probe_info.probe))
            scene.add(Point(BR_coords[0,:], radius=50, color='r'))
        if 'pos' in probe_info.probe:
            scene.add(Point(BR_coords[0,:], radius=50, color='b'))

## Slice the brain ##
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
scene.render(interactive=True, camera='sagittal', zoom=1.5)
# scene.render(interactive=False, camera='top', zoom=1)
# scene.render(interactive=True, camera=ccamera, zoom=1.2)
# camera options: 'top', 'sagittal', 'three_quarters'
# interactive=False to save a screenshot
# scene.render(interactive=False, camera='top', zoom=0.95)

## Save screenshot ##
# scene.screenshot(name=screenshot_name, scale=3)
# scene.close()

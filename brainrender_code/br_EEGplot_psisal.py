## Use conda env "brsdk" ##
import numpy as np
import pandas as pd
from pathlib import Path

# from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

from brainrender.scene import Scene
from brainrender.actors import Point
from brainrender import settings

################################################################################
## Set paths ##
EEG_info_csv_path = Path(
    r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\Templeton\NWB packaging\EEG_electrodes_info.csv"
)
plot_dir = Path(
    r"C:\Users\lesliec\OneDrive - Allen Institute\Shared Documents - Lab 328\Projects\Templeton\Psychedelics paper\brainrender"
)
## Set parameters ##
screenshot_name = "EEGelectrodes_topview_102025"
plot_title = "EEG electrodes"
show_regions = True # True/False to show the cortical regions underneath the electrodes
show_elecs = True # True/False to show the EEG electrodes as circles on the brain
show_crans = True # True/False to show approx craniotomies as circles on the brain
show_screws = True # True/False to show the gnd/ref screws as circles over the cb
elec_color = 'k'
elec_radius = 250 # these are roughly um, electrodes are 500 um in diameter
highlight_chs = [] # empty list if you don't want to highlight any electrodes
highlight_color = 'r'

################################################################################

## Set brainrender settings ##
settings.SHOW_AXES = False
pixel_scale = 25 # scale from 25 um CCF to brainrender coords

## Create the scene with correct atlas ##
scene = Scene(
    atlas_name="allen_mouse_25um", inset=False,
    title=plot_title, screenshots_folder=plot_dir,
)

## Load EEG information ##
EEG_ch_info = pd.read_csv(EEG_info_csv_path)
# Flip highlight ch numbers, due to brainrender backwards coordinates #
if len(highlight_chs) > 0:
    highlight_chs = [29-x for x in highlight_chs]

## Add brain regions ##
EEG_brain_regions = np.unique(EEG_ch_info.parent_acronym.values)
if show_regions:
    for regi in EEG_brain_regions:
        scene.add_brain_region(
            regi, alpha=1.0, silhouette=True, # hemisphere='left'
        )

## Add electrodes ##
if show_elecs:
    for indi, chi_info in EEG_ch_info.iterrows():
        if indi in highlight_chs:
            continue
        elec_coords = np.array([chi_info.x, chi_info.y, chi_info.z]) * pixel_scale
        elec_coords[1] -= 200
        # print('ch {:d}:'.format(indi))
        # print(elec_coords)
        scene.add(Point(elec_coords, color=elec_color, radius=elec_radius))

    ## Highlight one electrode ##
    if len(highlight_chs) > 0:
        for chi in highlight_chs:
            chi_info = EEG_ch_info.iloc[chi]
            elec_coords = np.array([chi_info.x, chi_info.y, chi_info.z]) * pixel_scale
            elec_coords[1] -= 200
            scene.add(Point(elec_coords, color=highlight_color, radius=elec_radius))

## Add skull screws ##
if show_screws:
    screw_coords = np.array([
        [11000, 1000, 7500],
        [11500, 800, 5700],
        [11000, 1000, 3900]
    ])
    for coordi in screw_coords:
        scene.add(Point(coordi, color='dimgray', radius=300))

## Add craniotomies ##
if show_crans:
    crans_coords = np.array([ # AP, DV, ML
        [8800, 300, 8000], # probe C: near chs 1&4
        [7800, 800, 9000], # probe D: near chs 3&4
        [6400, 400, 7600], # probe B: near chs 8&10
        [3600, 1200, 7200], # probe F: near chs 11&13
    ])
    for coordi in crans_coords:
        scene.add(Point(coordi, color='pink', radius=350))

## Render ##
# scene.render(interactive=True, camera='top', zoom=1)

## Save screenshot ##
scene.render(interactive=False, camera='top', zoom=1)
scene.screenshot(name=screenshot_name, scale=3)
scene.close()

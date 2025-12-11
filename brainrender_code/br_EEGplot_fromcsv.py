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
screenshot_name = "EEGelectrodes_topview"
plot_title = "EEG electrodes"
show_regions = True # True/False to show the cortical regions underneath the electrodes
show_elecs = True # True/False to show the EEG electrodes as circles on the brain
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
        scene.add(Point(elec_coords, color=elec_color, radius=elec_radius))

    ## Highlight one electrode ##
    if len(highlight_chs) > 0:
        for chi in highlight_chs:
            chi_info = EEG_ch_info.iloc[chi]
            elec_coords = np.array([chi_info.x, chi_info.y, chi_info.z]) * pixel_scale
            scene.add(Point(elec_coords, color=highlight_color, radius=elec_radius))

## Add skull screws ##
screw_coords = np.array([[10900, 1000, 7500], [10900, 1000, 3900]])
for coordi in screw_coords:
    scene.add(Point(coordi, color='dimgray', radius=400))

## Render ##
scene.render(interactive=True, camera='top', zoom=1)

## Save screenshot ##
# scene.render(interactive=False, camera='top', zoom=1)
# scene.screenshot(name=screenshot_name, scale=3)
# scene.close()

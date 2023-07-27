## Use conda env "br2" ##
import os
import numpy as np
import pandas as pd

from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

from brainrender.scene import Scene
from brainrender.actors import Point
from brainrender import settings
from vedo import shapes

## Show electrodes and craniotomies? ##
show_elecs = True

## Set brainrender settings ##
settings.SHOW_AXES = False

## EEG information ##
channel_list = np.arange(0, 30, dtype=int)

# coordinates relative to bregma (I pulled the coordinates from the image here:
# https://neuronexus.com/electrode-array/mouse-eeg/)
# ML: neg= mouse left, pos= mouse right
channel_ML = np.array([
    -4.05, -2.24, -1.0, -4.13, -2.88, -1.13, -4.05, -2.88, -1.12, -3.5,
    -2.12, -1.93, -0.5, -1.5, -0.5, 0.5, 1.5, 0.5, 1.93, 2.12,
    3.5, 1.12, 2.88, 4.05, 1.13, 2.88, 4.13, 1.0, 2.24, 4.05
])
channel_AP = np.array([
    -4.14, -4.14, -4.14, -3.04, -3.04, -3.04, -1.96, -1.96, -1.96, -0.48,
    -0.48, 1.04, 1.04, 2.3, 2.3, 2.3, 2.3, 1.04, 1.04, -0.48,
    -0.48, -1.96, -1.96, -1.96, -3.04, -3.04, -3.04, -4.14, -4.14, -4.14
])
coords = pd.DataFrame({'AP': channel_AP, 'ML': channel_ML})

## CCF and annotated volume ##
mcc = MouseConnectivityCache(resolution=25)
annot, annot_info = mcc.get_annotation_volume()
structure_tree = mcc.get_structure_tree()

## Finding bregma in CCF coordinates ##
mm_slice = 0.025 # mm, we are using CCF with 25 um resolution
cc_join_ind = 168 # AP_ind, I call this AP +1.1 mm
AP_zero_ind = cc_join_ind + int(1.1 / mm_slice)
# print('Bregma (AP) pixel ind: %d' % AP_zero_ind)
ML_zero_ind = np.shape(annot)[2]//2
# print('Bregma (ML) pixel ind: %d' % ML_zero_ind)
# find brain surface at bregma to find DV pixel
edge_indb = np.nonzero(annot[AP_zero_ind, int(np.shape(annot)[1]/2), :])[0][0]
bregma_surfaceML = np.arange(edge_indb, np.shape(annot)[2] - edge_indb)
bregma_surfaceDV = np.zeros_like(bregma_surfaceML)
for k, bsurML in enumerate(bregma_surfaceML):
    bregma_surfaceDV[k] = np.nonzero(annot[int(AP_zero_ind), :, int(bsurML)])[0][0]
DV_zero_ind = np.min(bregma_surfaceDV)
# print('Bregma (DV) pixel ind: %d' % DV_zero_ind)
CCF_bregma = np.array([AP_zero_ind, DV_zero_ind, ML_zero_ind])
bregma_actor = Point(pos=CCF_bregma*25, color='k', radius=50)

## Finding CCF coordinates of electrodes ##
coords['AP_pixel_ind'] = (AP_zero_ind - (coords['AP'] / mm_slice)).astype(int) # neg AP coords -> greater slice ind
coords['ML_pixel_ind'] = (ML_zero_ind + (coords['ML'] / mm_slice)).astype(int) # neg ML coords -> smaller slice ind (left)

## Find brain surface for each AP slice ##
new_ML_pix_inds = np.zeros(len(channel_list))
new_DV_pix_inds = np.zeros(len(channel_list))
for AP_pix_ind, slice_group in coords.groupby(['AP_pixel_ind']):

    # get surface of brain
    edge_ind = np.nonzero(annot[int(AP_pix_ind), int(np.shape(annot)[1]/2), :])[0][0]
    surfaceML = np.arange(edge_ind, np.shape(annot)[2] - edge_ind)
    surfaceDV = np.zeros_like(surfaceML)
    for k, surML in enumerate(surfaceML):
        surfaceDV[k] = np.nonzero(annot[int(AP_pix_ind), :, int(surML)])[0][0]
    surface_distance = np.concatenate(([0], np.cumsum(np.sqrt(np.diff(surfaceML)**2 + np.diff(surfaceDV)**2))))

    # Left side
    lelec = slice_group[slice_group['ML'] < 0].sort_values(['ML'], ascending=False)
    lseedML = lelec['ML'].iloc[0]
    lseedMLpix = lelec['ML_pixel_ind'].iloc[0]
    for index, row in lelec.iterrows():
        if row['ML_pixel_ind'] == lseedMLpix:
            new_ML_pix_inds[index] = lseedMLpix
            new_DV_pix_inds[index] = surfaceDV[surfaceML == lseedMLpix][0]
        else:
            seeddist = (lseedML - row['ML']) / mm_slice
            newind = np.argmin(np.abs((surface_distance - surface_distance[surfaceML == lseedMLpix]) + seeddist))
            new_ML_pix_inds[index] = surfaceML[newind]
            new_DV_pix_inds[index] = surfaceDV[newind]

    # Right side
    relec = slice_group[slice_group['ML'] > 0].sort_values(['ML'])
    rseedML = relec['ML'].iloc[0]
    rseedMLpix = relec['ML_pixel_ind'].iloc[0]
    for index, row in relec.iterrows():
        if row['ML_pixel_ind'] == rseedMLpix:
            new_ML_pix_inds[index] = rseedMLpix
            new_DV_pix_inds[index] = surfaceDV[surfaceML == rseedMLpix][0]
        else:
            seeddist = (rseedML - row['ML']) / mm_slice
            newind = np.argmin(np.abs((surface_distance - surface_distance[surfaceML == rseedMLpix]) + seeddist))
            new_ML_pix_inds[index] = surfaceML[newind]
            new_DV_pix_inds[index] = surfaceDV[newind]
coords['ML_pixel_ind'] = new_ML_pix_inds.astype(int)
coords['DV_pixel_ind'] = new_DV_pix_inds.astype(int)

## Use electrode CCF coords to find annotated brain region ##
# create empty lists to hold info (will add it to coords dataframe after loop)
structure_id = []
structure_name = []
parent_id = []
parent_name = []
structure_parent_acronym = []

# for loop through the coords dataframe
for indi, row in coords.iterrows():
    # choose first non-zero value in the annotated array at the AP, ML pixel inds
    non_zero_DV = np.nonzero(annot[int(row.AP_pixel_ind),:,int(row.ML_pixel_ind)])[0][0]
    struct_id_temp = annot[int(row.AP_pixel_ind), non_zero_DV, int(row.ML_pixel_ind)]
    # append structure id, name, parent info to empty lists
    structure_id.append(struct_id_temp)
    structure_name.append(structure_tree.get_structures_by_id([struct_id_temp])[0]['name'])
    parent_id.append(structure_tree.parents([struct_id_temp])[0]['id'])
    parent_name.append(structure_tree.parents([struct_id_temp])[0]['name'])
    structure_parent_acronym.append(structure_tree.parents([struct_id_temp])[0]['acronym'])

# add lists created to original dataframe
coords['structure_id'] = structure_id
coords['structure_name'] = structure_name
coords['parent_id'] = parent_id
coords['parent_name'] = parent_name

## Prep electrode and structure info for plotting with BrainRender ##
electrode_coords = np.array([coords.AP_pixel_ind.to_numpy(),
                             coords.DV_pixel_ind.to_numpy(),
                             coords.ML_pixel_ind.to_numpy()
                            ])
structure_list = list(set(structure_parent_acronym))

## Create the scene, populate and preprare for rendering ##
scene = Scene(
    inset=False, title='EEG array',
    screenshots_folder=r'C:\Users\lesliec\OneDrive - Allen Institute\data\plots\manuscript_figs\brainrender',
)

## Add brain regions under electrodes ##
for area in structure_list:
    scene.add_brain_region(area) # , add_labels=True)

## Add bregma ##
scene.add(bregma_actor)

if show_elecs:
    # Add electrodes ##
    for i in range(np.shape(electrode_coords)[1]):
        elec_actor = Point(pos=electrode_coords[:,i] * 25, color='goldenrod', radius=300)
        scene.add(elec_actor)

    ## Add craniotomies ##
    craniotomies = np.array([[1.7, 0.0, -1.55], [-1.1, 0.5, -1.6], [-3.6, 0.5, -2.7]])
    for crani in craniotomies:
        c_inds = ((CCF_bregma - (crani / mm_slice)) * 25).astype(int)
        crani_actor = Point(pos=c_inds, color='white', radius=260, alpha=0.3)
        scene.add(crani_actor)

## Add skull screws ##
screw_coords = np.array([[-5.6, 0.0, -1.8], [-5.6, 0.0, 1.8]])
for screwi in screw_coords:
    br_inds = ((CCF_bregma - (screwi / mm_slice)) * 25).astype(int)
    screw_actor = Point(pos=br_inds, color='dimgray', radius=400)
    scene.add(screw_actor)

## Add gray electrodes and black one over V1, ch 4 ##
# for i in range(np.shape(electrode_coords)[1]):
#     scene.add_sphere_at_point(electrode_coords[:,i]*25, radius=250, color='lightgray')
# scene.add_sphere_at_point(electrode_coords[:,4]*25, radius=250, color='k')

## Render ##
scene.render(interactive=False, camera='top', zoom=0.95)
## Save screenshot ##
scene.screenshot(name=r'EEG_chs_crans', scale=3)
scene.close()

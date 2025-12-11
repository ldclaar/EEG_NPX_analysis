## This code is STEP 1 in producing the brain figure with probes ##
## It requires a .csv file with a list of subjects to be included in the figure ##
## It uses the tbd_eeg repo to pull info about each probe within the experiment ##
## then puts the probe coordinates into another .csv file, which will be read ##
## by the code for STEP 2. ##

from glob import glob
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(r'C:\Users\lesliec\code')

from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

#### Set file names and parameters ####
data_dir = Path(r"B:\\") # location of the mouse data
subject_csv = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data\BrainStimpaper_IR_allsubjects.csv")

probe_csv_filename = r"BSpaperIR_08152024_probescoords.csv"
unit_csv_filename = r"BSpaperIR_08152024_unitscoords.csv"
save_csv_dir = Path(r"C:\Users\lesliec\OneDrive - Allen Institute\data")

ROI = None # if None, show all probes; ['AV', 'CL', 'MD', 'PO', 'RT', 'VAL', 'VPL', 'VPM', 'VM']
parentROI = None # ['TH']

makeunitscsv = False

# region_colors = {
#     'AV': 'HotPink',
#     'CL': 'Red',
#     'MD': 'Orange',
#     'PO': 'Gold',
#     'RT': 'Sienna',
#     'VAL': 'Purple',
#     'VPL': 'Blue',
#     'VPM': 'Cyan',
#     'VM': 'Green',
# }
BRCCF = 25 # to match the pixel scale to brainrender
###################################

#### Functions ####
def find_closest_region(sunit_info, struct_tree, annot):
    ## Finds a grey matter region above/below an unknown region ##
    Vind = sunit_info.CCF_DV
    vent_sip = struct_tree.get_structures_by_id([annot[sunit_info.CCF_AP, Vind, sunit_info.CCF_ML]])[0]['structure_id_path']
    while not struct_tree.structure_descends_from(vent_sip[-1], 8):
        Vind += 1
        vent_sip = struct_tree.get_structures_by_id([annot[sunit_info.CCF_AP, Vind, sunit_info.CCF_ML]])[0]['structure_id_path']

    Dind = sunit_info.CCF_DV
    dors_sip = struct_tree.get_structures_by_id([annot[sunit_info.CCF_AP, Dind, sunit_info.CCF_ML]])[0]['structure_id_path']
    while not struct_tree.structure_descends_from(dors_sip[-1], 8):
        Dind -= 1
        dors_sip = struct_tree.get_structures_by_id([annot[sunit_info.CCF_AP, Dind, sunit_info.CCF_ML]])[0]['structure_id_path']

    if (Vind - sunit_info.CCF_DV) <= (sunit_info.CCF_DV - Dind):
        return struct_tree.get_structures_by_id([vent_sip[-1]])[0]['acronym']
    elif (Vind - sunit_info.CCF_DV) > (sunit_info.CCF_DV - Dind):
        return struct_tree.get_structures_by_id([dors_sip[-1]])[0]['acronym']

def get_region_from_children(test_id, parent_id, struct_tree):
    try:
        child_ind = np.nonzero([
            struct_tree.structure_descends_from(test_id, x) for x in struct_tree.child_ids([parent_id])[0]
        ])[0][0]
        return struct_tree.get_structures_by_id([struct_tree.child_ids([parent_id])[0][child_ind]])[0]['acronym']
    except:
        return struct_tree.get_structures_by_id([parent_id])[0]['acronym']

def get_parent_region(region_acronym, struct_tree):
    areas_of_interest = {
        'SM-TH': ['AV', 'CL', 'MD', 'PO', 'PF', 'VAL', 'VPL', 'VPM', 'VM'],
    }

    reg_id = struct_tree.get_structures_by_acronym([region_acronym])[0]['id']
    if struct_tree.structure_descends_from(reg_id, 567):
        if struct_tree.structure_descends_from(reg_id, 315):
            return get_region_from_children(reg_id, 315, struct_tree)
        elif struct_tree.structure_descends_from(reg_id, 698):
            return 'OLF'
        elif struct_tree.structure_descends_from(reg_id, 1089):
            return get_region_from_children(reg_id, 1089, struct_tree)
        elif struct_tree.structure_descends_from(reg_id, 703):
            return get_region_from_children(reg_id, 703, struct_tree)
        elif struct_tree.structure_descends_from(reg_id, 477):
            return 'STR'
        elif struct_tree.structure_descends_from(reg_id, 803):
            return 'PAL'
        else:
            return 'unassigned'
    elif struct_tree.structure_descends_from(reg_id, 343):
        if struct_tree.structure_descends_from(reg_id, 1129):
            return 'TH'
            # if region_acronym == 'RT':
            #     return 'RT-TH'
            # elif region_acronym in areas_of_interest['SM-TH']:
            #     return 'SM-TH'
            # else:
            #     return 'other-TH'
        elif struct_tree.structure_descends_from(reg_id, 1097):
            return 'HY'
        else:
            return get_region_from_children(reg_id, 343, struct_tree)
    else:
        return 'unassigned'

def add_parent_region_to_df(unit_info_df, struct_tree, annot):
    ## First, make sure all names in region column correspond to a CCF region (removes nan values) ##
    adj_regions = unit_info_df['region'].values.copy()
    for indi, rowi in unit_info_df.iterrows():
        try:
            str_info = struct_tree.get_structures_by_acronym([rowi.region])[0]
        except KeyError:
            if rowi.depth <= 0: # unit was placed above brain
                new_region_id = annot[rowi.CCF_AP, np.nonzero(annot[rowi.CCF_AP, :, rowi.CCF_ML])[0][0], rowi.CCF_ML]
                adj_regions[indi] = struct_tree.get_structures_by_id([new_region_id])[0]['acronym']
            else:
                Lind = rowi.CCF_ML
                while annot[rowi.CCF_AP, rowi.CCF_DV, Lind] == 0:
                    Lind -= 1
                new_region_id = struct_tree.get_structures_by_id(
                    [annot[rowi.CCF_AP, rowi.CCF_DV, Lind]])[0]['structure_id_path'][-1]
                adj_regions[indi] = struct_tree.get_structures_by_id([new_region_id])[0]['acronym']
    unit_info_df['adj_region'] = adj_regions

    ## Second, re-assign any non-grey matter areas to the closest region ##
    adj_regions = unit_info_df['adj_region'].values.copy()
    for indi, rowi in unit_info_df.iterrows():
        reg_id = struct_tree.get_structures_by_acronym([rowi.adj_region])[0]['id']
        if not struct_tree.structure_descends_from(reg_id, 8):
            adj_regions[indi] = find_closest_region(rowi, struct_tree, annot)
    unit_info_df['adj_region'] = adj_regions

    ## Finally, assign a parent region to each adjusted CCF region ##
    parent_regions = unit_info_df['adj_region'].values.copy()
    for indi, rowi in unit_info_df.iterrows():
        parent_regions[indi] = get_parent_region(rowi.adj_region, struct_tree)
    unit_info_df['parent_region'] = parent_regions

    return unit_info_df.drop('adj_region', axis=1)
###################################

#### Loop through all subjects to get probe info ####
all_subexp = pd.read_csv(subject_csv)

all_subexp_probe_info = []
all_subexp_units_list = []
for indi, exprow in all_subexp.iterrows():
    print('{}: {}'.format(exprow.mouse, exprow.experiment))
    if not exprow.histology:
        print(" This subject doesn't have histology, skipping.\n")
        continue

    # data_paths = os.path.join(data_dir, '*', exprow.mouse, exprow.experiment, 'experiment1', 'recording1')
    data_paths = os.path.join(data_dir, exprow.mouse, exprow.experiment, 'experiment1', 'recording1')
    if len(glob(data_paths)) == 0:
        print(' This data path does not exist: {}.\n'.format(data_paths))
        continue

    exp = EEGexp(glob(data_paths)[0], preprocess=False, make_stim_csv=False)
    mcc = MouseConnectivityCache(resolution=exprow.CCFresolution)
    str_tree = mcc.get_structure_tree()
    annot, annot_info = mcc.get_annotation_volume()

    probe_list = [x.replace('_sorted', '') for x in exp.experiment_data if 'probe' in x]
    units_list = []
    for probei in probe_list:
        print(' {}'.format(probei))
        with open(exp.ephys_params[probei]['probe_info']) as data_file:
            data = json.load(data_file)
        if 'ccf_coord_ch' not in data.keys():
            print('  No locations for {}. skipping.'.format(probei))
            continue
        if (ROI is not None) and (np.sum([True if x in ROI else False for x in data['area_ch']]) == 0):
            print('  Missed target regions.')
            continue
        if exprow.CCFresolution != BRCCF:
            CCF25coords = np.array(data['ccf_coord_ch']) * exprow.CCFresolution / BRCCF # for a Line
        else:
            CCF25coords = np.array(data['ccf_coord_ch']) # for a Line
        all_subexp_probe_info.append([
            exprow.mouse, exprow.experiment, probei, probei[-1]==exprow.close_probe,
            CCF25coords[0,0], CCF25coords[0,1], CCF25coords[0,2],
            CCF25coords[-1,0], CCF25coords[-1,1], CCF25coords[-1,2]
        ])
        if makeunitscsv:
            ## Get units for probes that hit ROI ##
            select_units, peak_chs, unit_metrics = exp.get_probe_units(probei)
            unit_metrics['unit_name'] = [probei[-1] + str(x) for x in unit_metrics['cluster_id'].values]
            unit_metrics['probe'] = [probei] * len(unit_metrics)
            units_list.append(unit_metrics)

    if len(units_list) == 0:
        print('')
        continue
    all_select_units = pd.concat(units_list)
    all_units_info = []
    for ui, urow in all_select_units.iterrows():
        CCFcoords = [int(x) for x in urow['ccf_coord'].replace('[','').replace(']','').replace(' ','').split(',')]
        all_units_info.append([
            exprow.mouse, exprow.experiment, urow['unit_name'], urow['probe'], urow['area'], urow['spike_count'], urow['duration'],
            CCFcoords[0], CCFcoords[1], CCFcoords[2]
        ])
    all_units_df = pd.DataFrame(
        all_units_info, columns=['mouse', 'experiment', 'unit_name', 'probe', 'region', 'spike_count', 'spike_duration', 'CCF_AP', 'CCF_DV', 'CCF_ML']
    )
    ## Add parent region ##
    all_units_info_df = add_parent_region_to_df(all_units_df, str_tree, annot)
    ## Convert CCF coords ##
    all_units_info_df['CCF_AP'] = all_units_info_df['CCF_AP'].values  * exprow.CCFresolution / BRCCF
    all_units_info_df['CCF_DV'] = all_units_info_df['CCF_DV'].values  * exprow.CCFresolution / BRCCF
    all_units_info_df['CCF_ML'] = all_units_info_df['CCF_ML'].values  * exprow.CCFresolution / BRCCF
    ## Save units df ##
    all_subexp_units_list.append(all_units_info_df)

    print('')
all_subexp_probe_info_df = pd.DataFrame(
    all_subexp_probe_info, columns=['mouse', 'experiment', 'probe', 'close_to_stim', 'tipAP', 'tipDV', 'tipML', 'surfAP', 'surfDV', 'surfML']
)
if makeunitscsv:
    all_subexp_units = pd.concat(all_subexp_units_list)

## Save the probes .csv ##
all_subexp_probe_info_df.to_csv(os.path.join(save_csv_dir, probe_csv_filename), index=False)

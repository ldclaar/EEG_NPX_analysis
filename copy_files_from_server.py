import os
from glob import glob
from shutil import copy2, copytree, ignore_patterns
import time

################ To run ################
# conda activate base
# cd C:\Users\lesliec\code\EEG_NPX_analysis
# python copy_files_from_server.py
########################################

## Set params ##
copy_LFP = False


def copy_sorted_exp_from_server(experiment_dir, destination_folder):
    '''
    This copies the data in the given folder to the destination folder
    specified. It will create the mouse folder, if it does not exist. It does
    not copy the AP continuous.dat file, it creates an empty file instead.

    Inputs:
    --------
    experiment_dir : str
        Path for directory containing experiment data, this should point to the
        first folder (with the experiment name) inside each mouse folder.
    destination_folder : str
        Destination folder where each mouse folder will be created (if needed).
    '''
    ## Set some info ##
    AP_files_to_copy = [
        r'cluster_group.tsv',
        r'mean_waveforms.npy',
        r'metrics.csv',
        r'spike_clusters.npy',
        r'spike_times_master_clock.npy',
    ]

    mouse_name = os.path.basename(os.path.dirname(experiment_dir))
    print('{}: {}'.format(mouse_name, os.path.basename(experiment_dir)))

    ## Create the mouse and experiment name folder in destination ##
    new_mouse_folder = os.path.join(destination_folder, mouse_name)
    if not os.path.exists(new_mouse_folder):
        os.mkdir(new_mouse_folder)
    new_experiment_dir = os.path.join(new_mouse_folder, os.path.basename(experiment_dir))
    if not os.path.exists(new_experiment_dir):
        os.mkdir(new_experiment_dir)

    ## Copy everything except the probe folders ##
    copytree(
        experiment_dir,
        new_experiment_dir,
        ignore = ignore_patterns('probe*'),
        copy_function = copy2,
        dirs_exist_ok = True
    )

    ## Now find and copy contents of probe folders ##
    exp_folder = glob(experiment_dir + '\exper*', recursive=True)[0]
    new_exp_folder = glob(new_experiment_dir + '\exper*', recursive=True)[0]
    for folderi in os.listdir(exp_folder):
        if 'record' in folderi:
            continue
        print(' Copying {} folder.'.format(folderi))
        ## Copy everything except for AP continuous folder ##
        probe_folderi = os.path.join(exp_folder, folderi)
        new_probe_folderi = os.path.join(new_exp_folder, folderi)
        if not os.path.exists(new_probe_folderi):
            os.mkdir(new_probe_folderi)

        if copy_LFP:
            copytree(
                probe_folderi,
                new_probe_folderi,
                ignore = ignore_patterns('events', '*100.0', 'sample_*', 'timestamps.npy'),
                copy_function = copy2,
                dirs_exist_ok = True
            )
        else:
            copytree(
                probe_folderi,
                new_probe_folderi,
                ignore = ignore_patterns('events', '*100.0', '*100.1', 'sample_*', 'timestamps.npy'),
                copy_function = copy2,
                dirs_exist_ok = True
            )

        ## Create Neuropix-PXI-100.0 folder ##
        cont_folder = glob(probe_folderi + '\continuous', recursive=True)[0]
        AP_folder = glob(cont_folder + '\*100.0', recursive=True)[0]
        new_cont_folder = glob(new_probe_folderi + '\continuous', recursive=True)[0]
        new_AP_folder = os.path.join(new_cont_folder, os.path.basename(AP_folder))
        if not os.path.exists(new_AP_folder):
            os.mkdir(new_AP_folder)
        ## Copy the important AP files ##
        for filename in AP_files_to_copy:
            copy2(os.path.join(AP_folder, filename), new_AP_folder)
        ## Create the empty continuous file ##
        with open(os.path.join(new_AP_folder, 'continuous.dat'), 'w') as f:
            f.write('')

        if not copy_LFP:
            ## Create LFP (Neuropix-PXI-100.1) folder ##
            LFP_folder = glob(cont_folder + '\*100.1', recursive=True)[0]
            new_LFP_folder = os.path.join(new_cont_folder, os.path.basename(LFP_folder))
            if not os.path.exists(new_LFP_folder):
                os.mkdir(new_LFP_folder)
            ## Copy the master timestamps file ##
            copy2(os.path.join(LFP_folder, 'timestamps_master_clock.npy'), new_LFP_folder)
            ## Create the empty continuous file ##
            with open(os.path.join(new_LFP_folder, 'continuous.dat'), 'w') as f:
                f.write('')

    return

## Execute file copying ##
experiments_to_copy = [
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse657903\pilot_aw_psi_2023-01-13_12-18-22',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse666193\pilot_aw_2023-02-15_11-44-11',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse666193\pilot_aw_psi_2023-02-16_10-55-48',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse666193\pilot_ur_2023-02-17_12-22-51',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse666194\pilot_aw_2023-02-22_12-32-58',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse666194\pilot_aw_psi_2023-02-23_10-40-34',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse666194\pliot_ur_2023-02-24_11-19-43',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse654182\estim_vis_2022-12-01_10-33-50',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse654182\urethane_vis_2022-12-02_11-02-25',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse655956\estim_2022-12-15_10-07-59',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse655956\urethane_2022-12-16_10-45-18',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse631037\estim_2022-12-06_09-54-04',
    # r'\\allen\programs\mindscope\workgroups\templeton-psychedelics\mouse631037\urethane_2022-12-07_10-34-51',
    # r'P:\mouse669118\pilot_aw_2023-03-23_12-14-39',
    # r'P:\mouse669118\pilot_aw_psi_2023-03-24_09-55-33',
    # r'T:\zap-n-zip\EEG_exp\mouse638703\urethane_estim_2022-10-14_12-25-20',
    # r'P:\mouse654181\urethane_vis_2022-11-23_08-30-16',
    # r'P:\mouse655955\urethane_2022-12-14_10-38-00',
    # r'P:\mouse654181\estim_vis_2022-11-22_09-42-58',
    # r'T:\zap-n-zip\EEG_exp\mouse635397\estim_vis_2022-08-18_12-08-15',
    # r'T:\zap-n-zip\EEG_exp\mouse582386\urethane_2021-07-15_11-36-58',
    # r'P:\mouse669117\pilot_aw_2023-03-29_11-09-15',
    # r'P:\mouse669117\pilot_aw_psi_2023-03-30_11-37-07',
    # r'P:\mouse669117\pilot_ur_2023-03-31_11-51-53',
    # r'P:\mouse666196\pilot_aw_2023-03-15_12-29-06',
    # r'P:\mouse666196\pilot_aw_psi_2023-03-16_10-21-29',
    # r'P:\mouse673449\aw_2023-04-21_09-28-23',
    # r'P:\mouse673449\aw_psi_2023-04-19_11-23-26',
    # r'P:\mouse673449\aw_psi_d2_2023-04-20_10-05-31',
    # r'P:\mouse676726\aw_iso_2023-05-04_11-02-16',
    # r'P:\mouse676726\aw_psi_2023-05-03_11-08-22',
    # r'P:\mouse676727\aw_iso_2023-05-11_09-44-46',
    # r'P:\mouse676727\aw_psi_2023-05-10_09-49-12',
    # r'P:\mouse676727\urethane_2023-05-12_11-35-38',
    # r'R:\GAT_mice\mouse672785\EEGNPXspont_estim_2023-07-05_12-39-59',
    # r'R:\GAT_mice\mouse672789\EEGNPXspont_estim_2023-07-13_13-28-01',
    # r'P:\mouse678912\spont_aw_psi_2023-06-22_11-42-00',
    # r'P:\mouse678912\urethane_2023-06-23_11-08-17',
    # r'P:\mouse678913\spont_aw_psi_2023-06-29_12-49-40',
    # r'P:\mouse678913\urethane_2023-06-30_10-56-33',
    # r'P:\mouse689242\aw_iso_2023-07-20_10-52-57',
    # r'P:\mouse689242\aw_psi_2023-07-19_10-29-49',
    # r'P:\mouse689242\urethane_2023-07-21_12-32-25',
    # r'P:\mouse689239\aw_iso_2023-08-09_11-15-42',
    # r'P:\mouse689239\aw_psi_2023-08-10_11-26-36',
    # r'P:\mouse689239\urethane_2023-08-11_11-33-46',
    # r'P:\mouse689240\aw_iso_2023-08-18_10-03-39',
    # r'P:\mouse689240\aw_psi_2023-08-17_09-46-39',
    # r'P:\mouse692644\aw_iso_2023-09-06_11-27-02',
    # r'P:\mouse692644\aw_psi_2023-09-07_11-51-57',
    # r'P:\mouse692644\urethane_2023-09-08_11-15-18',
    # r'P:\mouse688277\aw_iso_2023-09-21_10-41-15',
    # r'P:\mouse688277\urethane_2023-09-22_12-04-23',
    # r'P:\mouse703062\aw_iso_2023-10-19_13-13-25',
    # r'P:\mouse703062\urethane_2023-10-20_12-00-46',
    # r'P:\mouse703063\aw_iso_2023-11-16_11-16-30',
    # r'P:\mouse703063\aw_psi_2023-11-15_11-08-12',
    # r'P:\mouse703063\urethane_2023-11-17_12-47-18',
    # r'P:\mouse703064\aw_iso_2023-11-29_11-23-30',
    # r'P:\mouse703064\aw_psi_2023-11-30_12-06-43',
    # r'P:\mouse703064\urethane_2023-12-01_11-20-15',
    # r'P:\mouse703065\aw_iso_2023-12-07_10-23-39',
    # r'P:\mouse703065\aw_psi_2023-12-06_11-04-39',
    # r'P:\mouse703065\urethane_2023-12-08_11-57-44',
    # r'P:\mouse709401\aw_iso_2023-12-13_09-55-07',
    # r'P:\mouse709401\aw_psi_2023-12-14_11-17-30',
    # r'P:\mouse709401\urethane_2023-12-15_11-03-00',
    # r'P:\mouse709400\aw_iso_2024-01-31_11-35-57',
    # r'P:\mouse709400\aw_ket_2024-02-01_11-12-34',
    # r'P:\mouse709400\urethane_2024-02-02_11-52-38',
    # r'P:\mouse709402\aw_iso_2024-02-15_10-26-16',
    # r'P:\mouse709402\aw_ket_2024-02-14_12-32-14',
    # r'P:\mouse709402\urethane_2024-02-16_11-15-43',
    # r'P:\mouse720762\aw_iso_2024-02-21_10-32-01',
    # r'P:\mouse720762\aw_ket_2024-02-22_10-43-35',
    # r'P:\mouse720762\urethane_2024-02-23_11-35-21',
    # r'P:\mouse724057\aw_sal_2024-04-03_10-32-05',
    # r'P:\mouse724057\aw_psi_2024-04-04_10-35-18',
    # r'P:\mouse730913\aw_sal_2024-04-24_10-43-30',
    # r'P:\mouse730913\aw_ket_2024-04-26_10-11-34',
    # r'P:\mouse730911\aw_sal_2024-05-01_11-57-16',
    # r'P:\mouse730911\aw_ket_2024-05-02_10-41-41',
    # r'P:\mouse735049\aw_sal_2024-05-22_11-05-25',
    # r'P:\mouse735049\aw_ket_2024-05-23_11-42-08',
    # r'P:\mouse709399\aw_iso_2024-01-24_10-26-14',
    # r'P:\mouse655955\estim_2022-12-13_10-05-19',
]
destination = r'F:\psi_exp' # r'F:\psi_exp', r'E:\GAT1_EEG_pilot'

for exp_diri in experiments_to_copy:
    start = time.time()
    copy_sorted_exp_from_server(exp_diri, destination)
    end = time.time()
    print('Time to copy: {:.2f} min\n'.format((end-start)/60))

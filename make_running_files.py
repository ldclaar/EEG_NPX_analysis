## This will go through multiple experiments to create the "running_signal.npy" and "running_timestamps_master_clock.npy" files.
import os
import numpy as np
from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp

## Set experiments to process ##
all_experiments = [
    r'F:\psi_exp\mouse631037\estim_2022-12-06_09-54-04\experiment1\recording1',
    r'F:\psi_exp\mouse631037\urethane_2022-12-07_10-34-51\experiment1\recording1',
]

## Do you want to overwrite any existing files?
### If True, it will process all experiments in list.
### If False, it will skip over any experiments that already have the processed running file.
overwrite_existing_files = False

## Loop through experiments and make running signal
for dataloc in all_experiments:
    exp = EEGexp(dataloc, preprocess=False, make_stim_csv=False)
    exp_tag = exp.experiment_folder[exp.experiment_folder.find('mouse')+12:exp.experiment_folder.find(str(exp.date.year))-1]
    print('{}: {}'.format(exp.mouse, exp_tag))

    ## Set file names ##
    running_file = os.path.join(exp.data_folder, 'running_signal.npy')
    running_ts_file = os.path.join(exp.data_folder, 'running_timestamps_master_clock.npy')

    ## Process running signal from sync file ##
    if os.path.exists(running_file):
        if overwrite_existing_files:
            print(' Loading running from sync and saving.')
            run_signal, run_timestamps = exp.load_running()
            np.save(running_file, run_signal, allow_pickle=False)
            np.save(running_ts_file, run_timestamps, allow_pickle=False)
        else:
            print(' Running file already exists, not overwriting.')
    else:
        print(' Loading running from sync and saving.')
        run_signal, run_timestamps = exp.load_running()
        np.save(running_file, run_signal, allow_pickle=False)
        np.save(running_ts_file, run_timestamps, allow_pickle=False)

    print('')

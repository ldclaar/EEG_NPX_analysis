### Plotting raw data from Npx recordings ###

## Here are some websites that have relevant info ##
# OpenEphys wiki, Neuropix-3a page: https://open-ephys.atlassian.net/wiki/spaces/OEW/pages/953548803/Neuropix-3a
# ecephys_spike_sorting: https://github.com/AllenInstitute/ecephys_spike_sorting
# Josh, et al. wrote this package to pre-process data for spike sorting. It is well-
# documented and has info about the different files that are created.
# I.e. https://github.com/AllenInstitute/ecephys_spike_sorting/blob/master/ecephys_spike_sorting/modules/extract_from_npx/README.md

# I run this in the tbd_eeg environment
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp

## Use EEGexp class to get experiment metadata ##
data_folder = r"F:\EEG_exp\mouse543394\estim1_2020-08-27_14-32-00\experiment1\recording1"
exp = EEGexp(data_folder, preprocess=False)

## Some info the EEGexp object has ##
print('Mouse: %s' % exp.mouse)
print('Experiment date: %s' % exp.date)
print('What data is in here?')
print(exp.experiment_data)

## Which probe to plot? ##
choose_probe = 'probeB'

## Define data paths ##
# data paths are now defined by the EEGexp object, so you can call them directly below

## Enter parameters for plotting ##
plot_type = 'eeg' # 'ap' or 'lfp' or 'eeg'
plot_chunk = 20 # number of channels per plot (it will plot all channels, just in separate plots for visibility)
plot_before = 0.02 # time to plot before event, s
plot_after = 0.08 # time to plot after event, s
plot_event = 'stim' # choose 'spont' to plot a random window of time or 'stim' to plot stimulus-triggered window

# if plot_event == 'spont'
spont_time = 7 # time in MINUTES to plot around if 'spont' is chosen
# if plot_event == 'stim'
event_ind = 5 # stim event to plot, must be integer
stim_type = 'biphasic' # 'monophasic' or 'biphasic'
stim_amp = 50 # current amplitude: 50, 70, 100?
sweep = 0 # choose sweep to look at

## Functions ##
# need to make a function that chooses stim event times
def get_stim_events(stim_table, stim_type, stim_param, sweep):
    if np.isin('stim_parameter', stim_table.columns):
        return stim_table[
                (stim_table['stim_type'] == stim_type) &
                (stim_table['stim_parameter'] == stim_param) &
                (stim_table['sweep'] == sweep)
                ].onset.values
    elif np.isin('amplitude', stim_table.columns):
        return stim_table[
                (stim_table['stim_type'] == stim_type) &
                (stim_table['amplitude'] == stim_param) &
                (stim_table['sweep'] == sweep)
                ].onset.values

## This section selects the data and loads it to memory ##
if plot_type == 'ap':
    numCh = exp.ephys_params[choose_probe]['num_chs']
    rawDatamm = np.memmap(exp.ephys_params[choose_probe]['ap_continuous'], dtype='int16', mode='r')
    datamm = np.reshape(rawDatamm, (int(rawDatamm.size/numCh), numCh))
    samp_rate = exp.ephys_params[choose_probe]['ap_sample_rate']
    timestamps = np.load(exp.ephys_params[choose_probe]['ap_timestamps'])
elif plot_type == 'lfp':
    numCh = exp.ephys_params[choose_probe]['num_chs']
    rawDatamm = np.memmap(exp.ephys_params[choose_probe]['lfp_continuous'], dtype='int16', mode='r')
    datamm = np.reshape(rawDatamm, (int(rawDatamm.size/numCh), numCh))
    samp_rate = exp.ephys_params[choose_probe]['lfp_sample_rate']
    timestamps = np.load(exp.ephys_params[choose_probe]['lfp_timestamps'])
elif plot_type == 'eeg':
    numCh = exp.ephys_params['EEG']['num_chs']
    rawDatamm = np.memmap(exp.ephys_params['EEG']['continuous'], dtype='int16', mode='r')
    datamm = np.reshape(rawDatamm, (int(rawDatamm.size/numCh), numCh))
    samp_rate = exp.ephys_params['EEG']['sample_rate']
    timestamps = np.load(exp.ephys_params['EEG']['timestamps'])
estim_log = pd.read_csv(exp.stimulus_log_file) # loads csv with estim onset times

## Create time axis for plotting ##
if plot_event == 'spont':
    plot_time = spont_time*60 # this value should be in seconds now
elif plot_event == 'stim':
    stim_times = get_stim_events(estim_log, stim_type, stim_amp, sweep)
    plot_time = stim_times[event_ind] # this value should be in seconds

## Collect the raw data from all channels in the time window specified ##
plot_inds = np.argwhere((timestamps > plot_time-plot_before) & (timestamps < plot_time+plot_after)).flatten()
plot_traces = datamm[plot_inds, :]
time_axis = (timestamps[plot_inds] - plot_time)*1000 # convert timestamps to ms

## For Npx ##
if plot_type == 'lfp' or plot_type == 'ap':
    ## Loads probe_info.json file to get DC offset for each ch ##
    with open(exp.ephys_params[choose_probe]['probe_info']) as data_file:
        data = json.load(data_file)
    offset = np.array(data['offset'])
    ## Remove DC offset and convert bits to microvolts ##
    plot_traces = (plot_traces - offset) * exp.ephys_params[choose_probe]['bit_volts']
elif plot_type == 'eeg':
    plot_traces = plot_traces[:,exp.EEG_channel_order] * exp.ephys_params['EEG']['bit_volts']
    numCh = plot_traces.shape[1]

## Select channels to plot ##
ch_chunks = np.arange(0, numCh, plot_chunk) # this plots chs 0 to 'numCh', which is 384, so it plots all chs

## Make the plots ##
for chx in ch_chunks:
    fig, ax = plt.subplots()
    sep = 0
    if chx+plot_chunk > numCh:
        plot_chunk = numCh - chx
    for chind in range(chx, chx+plot_chunk):
        ax.plot(time_axis, plot_traces[:,chind]+sep*200, 'k', linewidth=0.5)
        sep += 1

    ax.set(xlabel='Time (ms)', ylabel='Channel (separated by 200 uV)', title=('Plot of raw %s data' % plot_type))
    ax.get_yaxis().tick_left()
    plt.yticks(range(0, sep*200, 200), range(chx, chx+plot_chunk, 1), fontsize=6)

    plt.show()

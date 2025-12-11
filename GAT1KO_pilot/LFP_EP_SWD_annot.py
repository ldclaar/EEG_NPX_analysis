import argparse
import json
import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
sys.path.append(r'C:\Users\lesliec\code')
from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp
from tbd_eeg.tbd_eeg.data_analysis.Utilities.utilities import get_evoked_traces

# Function to generate a plot
def create_plot(traces, filtamp, timestamps, mean_amp):
    # Create the plot
    fig, ax = plt.subplots(figsize=(8,4), constrained_layout=True)
    ax.axvspan(0, 0.002, color='g', alpha=0.2)
    ax.plot(timestamps, traces, c='k', linewidth=1.0, alpha=0.6)
    ax.plot(timestamps, filtamp, c='r', linewidth=1.5, alpha=0.8)
    ax.axhline(mean_amp, color='m', linestyle='dashed', alpha=0.4)
    ax.set_xlabel('Time from stim onset (s)')
    ax.set_ylabel('Voltage (uV)')
    ax.set_title('Raw EP on LFP')
    ax.set_xlim([-2.0, 2.0])
    ax.set_ylim([-2800, 2800])

    # Show the plot
    plt.show()

# Function to ask the user for an annotation
def get_annotation_extra():
    valid = True
    while valid:
        annotation = input("Enter your annotation, is this in an SWD wave (enter t, f, or a): ")
        if annotation in ['t', 'f', 'a']:
            valid = False
        elif annotation == '':
            annotation = 'f'
            valid = False
        else:
            print("Try again, must be t, f, or a.")
    return annotation

# Function to ask the user for an annotation
def get_annotation():
    valid = True
    while valid:
        annotation = input("Enter your annotation, is this in an SWD (0 or 1): ")
        if annotation in ['0', '1']:
            valid = False
        elif annotation == '':
            annotation = '0'
            valid = False
        else:
            print("Try again, must be 0 or 1.")
    return annotation

# Function to save the annotation
def save_annotation_extra(annotation, annotations):
    annotations.append(annotation)
    print("Annotation saved!")
    return annotations

# Function to save the annotation
def save_boolean_annotation(annotation, annotations):
    annotations.append(int(annotation))
    print("Annotation saved!")
    return annotations

# Function to load EEGexp and get EEG event traces
def load_LFP_data(file_path):
    exp = EEGexp(file_path, preprocess=False, make_stim_csv=False)
    print('Loading EEGexp: {} - {}'.format(exp.mouse, exp.data_folder[exp.data_folder.find('mouse')+12:exp.data_folder.find('experiment')-1]))
    stim_log = pd.read_csv(exp.stimulus_log_file).astype({'parameter': str})
    ## Somehow need to pick a probe/ch in SSp ##
    probe_list = [x.replace('_sorted', '') for x in exp.experiment_data if 'probe' in x]
    for probei in probe_list:
        print(probei)
        with open(exp.ephys_params[probei]['probe_info']) as data_file:
            data = json.load(data_file)
        npx_allch = np.array(data['channel'])
        probe_areas = np.array(data['area_ch'])
        print(np.unique(probe_areas))
        SSp_mask = np.array([True if 'SSp' in x else False for x in probe_areas])
        l5_mask = np.array([True if '5' in x else False for x in probe_areas])
        print(npx_allch[SSp_mask * l5_mask])
        print('')

    probe_name = input("Choose probe ('probeX'): ")
    plot_ch = input("Choose channel: ")
    plot_ch = int(plot_ch)

    ## Load LFP as memmap ##
    lfp_ts = np.load(exp.ephys_params[probe_name]['lfp_timestamps'])
    lfp_data_mm = np.memmap(exp.ephys_params[probe_name]['lfp_continuous'], dtype='int16', mode='r').reshape(
        (len(lfp_ts), exp.ephys_params[probe_name]['num_chs']))

    raw_lfp_ch = lfp_data_mm[:, plot_ch] * exp.ephys_params[probe_name]['bit_volts']
    ## Apply bandpass filter (reverse, filter in 1 direction, and reverse again to correct for analog filter phase shift) ##
    hardware_filter = signal.butter(1, Wn=[3.0, 10.0], btype='band', fs=exp.ephys_params[probe_name]['lfp_sample_rate'])
    lfp_filt_ch = np.flip(signal.lfilter(*hardware_filter, np.flip(raw_lfp_ch)))
    ## Hilbert transform ##
    analytic_signal = signal.hilbert(lfp_filt_ch)
    amplitude_envelope = np.abs(analytic_signal)
    mean_amp = np.mean(amplitude_envelope)

    ## Get event traces ##
    event_window = [-2.0, 2.0]
    plot_events = stim_log[stim_log['stim_type'] == 'biphasic']
    event_LFPch, event_ts = get_evoked_traces(
        raw_lfp_ch[:, None], lfp_ts, plot_events.onset.values, -event_window[0], event_window[1], exp.ephys_params[probe_name]['lfp_sample_rate'])
    event_LFPch = np.squeeze(event_LFPch)
    event_ampenv, ae_ts = get_evoked_traces(
        amplitude_envelope[:, None], lfp_ts, plot_events.onset.values, -event_window[0], event_window[1], exp.ephys_params[probe_name]['lfp_sample_rate'])
    event_ampenv = np.squeeze(event_ampenv)

    annotations_file_path = os.path.join(exp.data_folder, 'EP_in_SWD_LFP_TF2.npy')
    return event_LFPch, event_ts, event_ampenv, mean_amp, annotations_file_path

# Function to save annotations to a file
def save_annotations_to_file(annotations, file_path):
    annot_array = np.array(annotations)
    print('Number of annotations: {:d}'.format(len(annot_array)))
    np.save(file_path, annot_array)
    print(f"Annotations saved to {file_path}!")

# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Plot EPs in the LFP and annotate SWDs.")
    parser.add_argument('file', type=str, help="Path of the recording folder.")
    args = parser.parse_args()

    # Load existing annotations from the provided file
    event_traces, event_ts, event_ampenv, mean_amp, annotations_file = load_LFP_data(args.file)

    # Loop for a fixed number of iterations
    annotations = []
    # for i in range(10):
    for i in range(event_traces.shape[1]):
        print(f"Annotating plot {i + 1}/{event_traces.shape[1]}")
        create_plot(event_traces[:,i], event_ampenv[:,i], event_ts, mean_amp)  # Create and display the plot

        # annotation = get_annotation_extra()  # Get user input for annotation
        # annotations = save_annotation_extra(annotation, annotations)  # Save annotation
        annotation = get_annotation()  # Get user input for annotation
        annotations = save_boolean_annotation(annotation, annotations)  # Save annotation

    # Save annotations to the specified file
    save_annotations_to_file(annotations, annotations_file)

# Run the main function
if __name__ == "__main__":
    main()

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import time
sys.path.append(r'C:\Users\lesliec\code')
from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp

# Function to generate a plot
def create_plot(traces, timestamps):
    rect_mean = np.mean(np.abs(traces), axis=1)
    gfp = np.std(traces, axis=1)

    # Create the plot
    fig, ax = plt.subplots(figsize=(8,4), constrained_layout=True)
    ax.axvspan(0, 0.002, color='g', alpha=0.2)
    ax.plot(timestamps, traces, c='k', linewidth=0.8, alpha=0.4)
    ax.plot(timestamps, rect_mean, c='c', linewidth=1.5, alpha=0.8)
    ax.plot(timestamps, gfp, c='m', linewidth=1.5, alpha=0.8)

    ax.set_xlabel('Time from stim onset (s)')
    ax.set_ylabel('Voltage (uV)')
    ax.set_title('Raw EP')
    ax.set_xlim([-2.0, 2.0])
    ax.set_ylim([-2000, 2000])

    # Show the plot
    plt.show()

# Function to ask the user for an annotation
def get_annotation():
    valid = True
    while valid:
        annotation = input("Enter your annotation, is this in an SWD: ")
        if annotation in ['0', '1']:
            valid = False
        elif annotation == '':
            annotation = '0'
            valid = False
        else:
            print("Try again, must be 0 or 1.")
    return annotation

# Function to save the annotation
def save_annotation(annotation, annotations):
    annotations.append(int(annotation))
    print("Annotation saved!")
    return annotations

# Function to load EEGexp and get EEG event traces
def load_EEGexp_data(file_path):
    exp = EEGexp(file_path, preprocess=False, make_stim_csv=False)
    print('Loading EEGexp: {} - {}'.format(exp.mouse, exp.data_folder[exp.data_folder.find('mouse')+12:exp.data_folder.find('experiment')-1]))

    all_EEG_traces = np.load(os.path.join(exp.data_folder, 'evoked_data', 'event_EEGtraces.npy'))
    EEG_event_timestamps = np.load(os.path.join(exp.data_folder, 'evoked_data', 'event_EEGtraces_times.npy'))

    annotations_file_path = os.path.join(exp.data_folder, 'EP_in_SWD.npy')
    return all_EEG_traces, EEG_event_timestamps, annotations_file_path

# Function to save annotations to a file
def save_annotations_to_file(annotations, file_path):
    annot_array = np.array(annotations)
    print('Number of annotations: {:d}'.format(len(annot_array)))
    np.save(file_path, annot_array)
    print(f"Annotations saved to {file_path}!")

# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Plot EPs and annotate SWDs.")
    parser.add_argument('file', type=str, help="Path of the recording folder.")
    args = parser.parse_args()

    # Load existing annotations from the provided file
    event_traces, event_ts, annotations_file = load_EEGexp_data(args.file)

    # Loop for a fixed number of iterations
    annotations = []
    # for i in range(10):
    for i in range(event_traces.shape[2]):
        print(f"Annotating plot {i + 1}/{event_traces.shape[2]}")
        create_plot(event_traces[:,:,i], event_ts)  # Create and display the plot

        annotation = get_annotation()  # Get user input for annotation
        annotations = save_annotation(annotation, annotations)  # Save annotation

    # Save annotations to the specified file
    save_annotations_to_file(annotations, annotations_file)

# Run the main function
if __name__ == "__main__":
    main()

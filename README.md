# EEG_NPX_analysis

Code for analyzing EEG and Neuropixels (NPX) data.

### Miscellaneous code in main folder
- [copy_files_from_server](copy_files_from_server.py): can copy multiple experiments from a specified server location to a local folder. It copies only the necessary files for normal analysis, so it does not copy the NPX AP "continuous.dat" file that is gigantic.
- [multisub_extract_evoked_responses](multisub_extract_evoked_responses.ipynb): my attempt at developing a standard pre-processing and data epoching method. It processes the running signal from the sync file, the EEG signal, and accumulates all good units from all probes, then saves the created files in an "evoked_data" folder within the "recording1" folder for easy access and quick loading later. Many recent scripts that I write access these pre-processed files, instead of the raw data.
- [OpenEphys_message_timestamps](OpenEphys_message_timestamps.ipynb): gets the synced timestamps of all messages entered into Open Ephys during the experiment. This has also been added to the tbd_eeg repository.
- [respiration_signal_testing](respiration_signal_testing.ipynb): loads the new respiration signal (thermistor) and performs basic processing and peak finding to create a respiration rate signal. May need further development to be robust across subjects.
- [test_pupilvideo_synctimes](test_pupilvideo_synctimes.ipynb): investigates pupil video frame counts and compares it to the sync pulses. Parsa had identified some videos that had a mismatch. This attempts to figure out which frames correspond to which sync pulses.
- [timestamp_alignment_ALL](timestamp_alignment_ALL.ipynb): practice code for aligning all timestamps to the sync clock. Can be useful for troubleshooting timestamp alignment errors.
- [wheel_signal](wheel_signal.ipynb): practice code for extracting the running speed from the wheel signal recorded by the sync computer...likely will be useful to further optimize this algorithm and then transfer it into the tbd_eeg repository.

### Folders

1. **CCF_related_analyses**: contains code that interacts with the CCF, for example
basic plotting, finding NPX probe locations/angles, and finding CCF regions
associated with the EEG electrodes.

2. **EEG_based_analyses**: contains code that focuses on analyzing the EEG signals.
    - [EEG_signal_test](EEG_based_analyses/EEG_signal_test.ipynb): used to analyze the signal tests we run with visual stimuli, plots visual evoked potentials and basic spectral analysis.
    - [EEG_ch_quality](EEG_based_analyses/EEG_ch_quality.ipynb): used to visualize evoked potentials from experiments to determine which channels contain artifact/noise.
    - [spatial_interp](EEG_based_analyses/spatial_interp.ipynb): can create heat maps of EEG data spatially interpolated to create topographical map of voltages.
    - [spatiotemp_movie](EEG_based_analyses/spatiotemp_movie.ipynb): attempt to create a movie of spatially interpolated EEG voltage over time, sometimes creates choppy videos.
    - [using_MNE_package](EEG_based_analyses/using_MNE_package.ipynb): MNE is a package for analyzing human EEG data in standardized formats with a lot of available tools (i.e., for coherence, time-frequency analysis, etc.). This code shows how to format our data so that it can be loaded into MNE.

3. **eLife_manuscript_analysis_notebooks**: contains code that was used to analyze data and create figures for the eLife CTC manuscript. Is also located in the [tbd_eeg repository](https://github.com/AllenInstitute/tbd_eeg/tree/master/tbd_eeg/data_analysis/eLife_2023_analysis).

4. **GAT1KO_pilot**: contains code used to look at data from GAT1-KO mice, specifically identifying spike-wave discharges and plotting EEG/NPX data related to those events.

5. **NPX_based_analyses**: contains code that predominantly focuses on NPX data (units, LFP, and CSD).
    - [brain_states_analysis](NPX_based_analyses/brain_states_analysis.ipynb): used to analyze all brain states (as of mid 2023: awake, saline, psilocybin, isoflurane, and urethane) and make comparisons across them. Mainly looks at unit metrics (firing rate, latency, etc.) across different brain regions.
    - [extract_unit_event_spikes](NPX_based_analyses/extract_unit_event_spikes.ipynb): extracts event-related spike and burst times for regions of interest across all probes. It saves this data in an "evoked_data" folder within the "recording1" folder for easy access and quick loading later. **I used this script to create the files that I accessed with the eLife manuscript analysis scripts.**
    - [find_parent_brain_region](NPX_based_analyses/find_parent_brain_region.ipynb): a script that can read the CCF locations and assign them to a higher brain area (a parent region). For example, it will assign "MOs5" to "MO" or "VAL" to "SM-TH". Can be useful when trying to aggregate data across areas without splitting into too many small higher-order areas (like different layers). This was made into a function and used in [multisub_extract_evoked_responses](multisub_extract_evoked_responses.ipynb).

6. **NWB_packaging**: contains tutorial notebooks from PyNWB and some practice files integrating the tutorials with our data/tbd_eeg repository.

7. **OLD**: self-explanatory :)

8. **stim_log_testing**: contains code for reading various stimulus log files and matching up event times recorded by the sync computer, this can be useful for troubleshooting issues with making the "stim_log.csv" file.

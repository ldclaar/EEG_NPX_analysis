# EEG_NPX_analysis

Code for analyzing EEG and Neuropixels (NPX) data.

### Folders

1. CCF_related_analyses: contains code that interacts with the CCF, for example
basic plotting, finding NPX probe locations/angles, and finding CCF regions
associated with the EEG electrodes.

2. EEG_based_analyses: contains code that focuses on analyzing the EEG signals.
- [EEG_signal_test](EEG_based_analyses/EEG_signal_test.ipynb): used to analyze the signal tests we run with visual stimuli, plots visual evoked potentials and basic spectral analysis.
- [EEG_ch_quality](EEG_based_analyses/EEG_ch_quality.ipynb): used to visualize evoked potentials from experiments to determine which channels contain artifact/noise.
- [spatial_interp](EEG_based_analyses/spatial_interp.ipynb): can create heat maps of EEG data spatially interpolated to create topographical map of voltages.
- [spatiotemp_movie](EEG_based_analyses/spatiotemp_movie.ipynb): attempt to create a movie of spatially interpolated EEG voltage over time, sometimes creates choppy videos.
- [using_MNE_package](EEG_based_analyses/using_MNE_package.ipynb): MNE is a package for analyzing human EEG data in standardized formats with a lot of available tools (i.e., for coherence, time-frequency analysis, etc.). This code shows how to format our data so that it can be loaded into MNE.

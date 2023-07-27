## Movie loading and making animated plots

# To make animated plots you need to install FFmpeg, here is a link to instructions
# https://www.wikihow.com/Install-FFmpeg-on-Windows

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib import animation
from scipy import signal

sys.path.append(r'C:\Users\lesliec\code')
from tbd_eeg.tbd_eeg.data_analysis.eegutils import EEGexp
from tbd_eeg.tbd_eeg.data_analysis.Utilities.behavior_movies import Movie # imports Movie class

# data location
data_folder = r"E:\eeg_pilot\mouse496220\audio_vis4_2020-06-18_13-49-17\recording1"

# make experiment object
exp = EEGexp(data_folder)

# make Movie object for body, pupil, and face
bodymovie = Movie(filepath=exp.bodymovie_file,
                 sync_filepath=exp.sync_file,
                 sync_channel='behavior_camera'
                 )
pupilmovie = Movie(filepath=exp.pupilmovie_file,
                  sync_filepath=exp.sync_file,
                  sync_channel='eye_camera'
                  )
facemovie = Movie(filepath=exp.facemovie_file,
                 sync_filepath=exp.sync_file,
                 sync_channel='face_camera'
                 )

# load EEG/timestamps
EEGdata, EEGtime = exp.load_eegdata()

# choose one electrode to plot
plot_elec = 8
elec_eeg = EEGdata[:, plot_elec]

# spectral analysis (makes it easy to see struggling-noise)
frex, time, pwr = signal.spectrogram(elec_eeg, exp.sample_rate)
spectime = time + EEGtime[0] # timestamps for power spectrum aligned to EEGtime

frinds = frex < 1000 # plot frequencies below 1000 Hz
pwr_spec = pwr[frinds,:]

# choose a time period for the animation
movie_start = 1337.0 # seconds
movie_end = 1347.0

# find indices of data in time window
eeginds = np.argwhere((EEGtime >= movie_start) & (EEGtime <= movie_end)).flatten()
specinds = np.argwhere((spectime >= movie_start) & (spectime <= movie_end)).flatten()

# find movie timestamps (using body movie)
bodymovietimes = bodymovie.sync_timestamps[np.argwhere((bodymovie.sync_timestamps >= movie_start) & (bodymovie.sync_timestamps <= movie_end)).flatten()]

# write a function to update the plot frame for each timestamp you give it
def update(frame):
    current_time = bodymovietimes[frame]
    # body cam movie
    bax.set_data(bodymovie.get_frame(time=current_time)) # the .get_frame() function grabs a movie frame closest to the time you give it
    # eeg plot
    eegline.set_data([current_time, current_time], [0,1]) # this moves the green bar to follow time
    # spectrogram
    specline.set_data([current_time, current_time], [0,1])
    return fig

# initialize plot
fig = plt.figure(figsize=(10, 4))
fig.patch.set_facecolor('whitesmoke')

timezero = bodymovietimes[0]

# make grid for subplots
gs = GridSpec(2, 2, figure=fig)
ax_body = fig.add_subplot(gs[:, 0])
ax_eeg = fig.add_subplot(gs[0, 1])
ax_spec = fig.add_subplot(gs[1, 1], sharex=ax_eeg)

# body cam movie
bax = ax_body.imshow(bodymovie.get_frame(time=timezero))
ax_body.get_xaxis().set_visible(False)
ax_body.get_yaxis().set_visible(False)

# EEG plot
ax_eeg.plot(EEGtime[eeginds], elec_eeg[eeginds], 'r', linewidth=0.5)
ax_eeg.set_xlim((EEGtime[eeginds[0]], EEGtime[eeginds[-1]]))
ax_eeg.set_ylim((-300, 300))
ax_eeg.set_ylabel('EEG signal (uV)')
eegline = ax_eeg.axvline(x=timezero, color='green', linewidth=2)

# Spectrogram
ax_spec.pcolormesh(spectime[specinds], frex[frinds], pwr_spec[:,specinds], cmap='YlOrRd', vmin=0, vmax=5)
ax_spec.set_ylabel('Freq')
ax_spec.set_xlabel('Time (s)')
specline = ax_spec.axvline(x=timezero, color='green', linewidth=2)

gs.tight_layout(fig)

# animate plot
anim = animation.FuncAnimation(fig, update, init_func=None, frames=len(bodymovietimes), interval=17, blit=False)
# the "interval" argument has something to do with how much time is between each of your frames

# save movie to mouse data folder
movie_name = os.path.join(exp.data_folder, 'sample_movie.mp4')
anim.save(movie_name, writer='ffmpeg', fps=30, extra_args=['-vcodec', 'libx264'], dpi=300)

plt.show()

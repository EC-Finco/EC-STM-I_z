import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pybaselines
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks, peak_prominences, peak_widths


def preproc(path_in, file_input):
    path = path_in + "/" + file_input  # creates path to open files
    # imports file into dataframe and creates dataframe for
    spectra = pd.read_csv(path, delimiter=" ", header=13, names=["Position", "Current"], engine='python', skipfooter=1)
    peaks = pd.DataFrame()
    # module to crop saturated currents
    maxcurrent = np.amax(spectra.Current)
    spectra = spectra[spectra.Current < maxcurrent]  # to rethink
    current = uniform_filter1d(spectra.Current, 10)  # smoothing
    baseasls = pybaselines.whittaker.asls(current, lam=10 ** 4, p=0.02)[0]  # baseline calculation with asls
    residuals = current - baseasls  # residual calculation
    spectra['Residuals'] = residuals
    # peak finding
    peak, _ = find_peaks(residuals, prominence=0.2)  # collect the indices of peaks with a minimum prominence of 0.2
    peakpos = spectra.Position[peak]
    # peak validation
    prominences = peak_prominences(residuals, peak)[0]
    widths = peak_widths(residuals, peak)[0]  # width in number of points
    density = np.amax(spectra.Position) / len(spectra.Position)
    widths = widths * density  # width in nm
    heights = peak_widths(residuals, peak)[1]
    peaks['Position (nm)'] = peakpos
    peaks['Prominence'] = np.transpose(prominences)
    peaks['Width (nm)'] = np.transpose(widths)
    peaks['Height (nA)'] = np.transpose(heights)
    plt.figure()
    plt.plot(spectra.Position, spectra.Current)
    plt.plot(spectra.Position, spectra.Residuals)
    plt.plot(spectra.Position, baseasls)
    plt.title(file_input)
    plt.xlabel('Position / nm')
    plt.ylabel('Current / nA')
    plt.show()
    # data export: 1) corrected spectra
    headerdata: list[str] = ["Position (nm)", "Current (nA)", "Residuals (nA)"]
    path_spectra = path_in + "/preprocessed spectra/"
    path_out = path_spectra + file_input.replace(".ts", "-spectra.txt")
    with open(path_out, 'a') as f:
        df_spectra = spectra.to_string(header=headerdata, index=False)
        f.write(df_spectra)
    # data export: 2)peak features
    headerpeaks = ["Position (nm)", "Prominence", "Width", "Height"]
    path_peaks = path_in + "/peak data/"
    path_out = path_peaks + file_input.replace(".ts", "-peaks.txt")
    with open(path_out, 'a') as f:
        df_peaks = peaks.to_string(header=headerpeaks, index=False)
        f.write(df_peaks)
    return spectra, peaks

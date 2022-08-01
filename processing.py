import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pybaselines
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks, peak_prominences, peak_widths


def preproc_asls(path_in, file_input, export):
    path = path_in + "/" + file_input  # creates path to open files
    # imports file into dataframe and creates dataframe for
    spectra = pd.read_csv(path, delimiter=" ", header=13, names=["Position", "Current"], engine='python', skipfooter=1)
    # module to crop saturated currents
    maxcurrent = np.amax(spectra.Current)
    spectra = spectra[spectra.Current < maxcurrent]  # to rethink
    current = uniform_filter1d(spectra.Current, 10)  # smoothing
    baseasls = pybaselines.whittaker.asls(current, lam=10 ** 6, p=0.02)[0]  # baseline calculation with asls
    residuals = current - baseasls  # residual calculation
    residuals = residuals[spectra.Current < maxcurrent]
    spectra['Residuals'] = residuals
    spectra['Baseline'] = baseasls
    # plotting(spectra, file_input, export)
    peaks = peak_extraction(spectra)
    if export == 'y':
        exporter(path_in, file_input, spectra, peaks)
    return spectra, peaks


def preproc_derpsalsa(path_in, file_input, export):
    path = path_in + "/" + file_input  # creates path to open files
    # imports file into dataframe and creates dataframe for
    spectra = pd.read_csv(path, delimiter=" ", header=13, names=["Position", "Current"], engine='python', skipfooter=1)
    # module to crop saturated currents
    maxcurrent = np.amax(spectra.Current)
    spectra = spectra[spectra.Current < maxcurrent]  # to rethink
    current = uniform_filter1d(spectra.Current, 20)  # smoothing
    basederpsalsa = pybaselines.whittaker.derpsalsa(current, lam=2000, p=0.002)[0]
    # baseline calculation with derpsalsa
    residuals = current - basederpsalsa  # residual calculation
    residuals = residuals[spectra.Current < maxcurrent]  # residual cropping
    index = []
    l = len(residuals)
    for i in range(l):
        index.append(str(i+1))
    spectra['Residuals'] = residuals
    spectra['Baseline'] = basederpsalsa
    spectra.index = index
    peaks = peak_extraction(spectra)
    plotting(spectra, peaks, file_input, path_in, export)
    if export == 'y':
        exporter(path_in, file_input, spectra, peaks)
    return spectra, peaks


def plotting(spectra, peaks, file_input, path_in, export):
    plt.figure()
    plt.plot(spectra.Position, spectra.Current, label="measure")
    plt.plot(spectra.Position, spectra.Residuals, label="residual")
    plt.plot(spectra.Position, spectra.Baseline, label="baseline")
    plt.plot(peaks.Position, spectra.Residuals[peaks.Index], "bo", label="peaks")
    plt.title(file_input)
    plt.xlabel('Position / nm')
    plt.ylabel('Current / nA')
    if export == 'y':
        path = path_in + "/plots/" + file_input.replace(".ts", "-plot.jpg")  # path for plots
        plt.savefig(path, format='jpg')  # save figure in jpg format
    plt.show()


def peak_extraction(spectra):
    peaks = pd.DataFrame()
    # peak finding
    peaklist, _ = find_peaks(spectra.Residuals, prominence=0.5, distance=20)
    # collect the indices of peaks with a minimum prominence of 0.5 and minimum distance of 20 points
    peak_index = np.array(peaklist, dtype=int)  # converting list into array
    # print(peak)
    peakpos = spectra.Position[peak_index]
    # peak validation
    prominences = peak_prominences(spectra.Residuals, peak_index)[0]
    widths = peak_widths(spectra.Residuals, peak_index)[0]  # width in number of points
    density = np.amax(spectra.Position) / len(spectra.Position)
    widths = widths * density  # width in nm
    heights = peak_widths(spectra.Residuals, peak_index)[1]
    peaks['Index'] = peak_index
    peaks['Position'] = np.array(peakpos)
    peaks['Prominence'] = np.transpose(prominences)
    peaks['Width'] = np.transpose(widths)
    peaks['Height'] = np.transpose(heights)
    return peaks


def exporter(path_in, file_input, spectra, peaks):
    # data export: 1) corrected spectra
    headerdata: list[str] = ["Position (nm)", "Current (nA)", "Residuals (nA)", "Baseline (nA)"]
    path_spectra = path_in + "/preprocessed spectra/"
    path_out = path_spectra + file_input.replace(".ts", "-spectra.txt")
    with open(path_out, 'a') as f:
        df_spectra = spectra.to_string(header=headerdata, index=False)
        f.write(df_spectra)
    # data export: 2)peak features
    headerpeaks = ["Index", "Position (nm)", "Prominence", "Width", "Height"]
    if not peaks.empty:
        path_peaks = path_in + "/peak data/"
        path_out = path_peaks + file_input.replace(".ts", "-peaks.txt")
        peaks.to_csv(path_out, header=True, sep="\t", index=False)

#####       FUNCTIONS FOR HISTOGRAM         #####
def proc_hist(files, export="y"):
    path = os.getcwd()
    chunk = pd.DataFrame()
    peaks = pd.DataFrame()
    chunks = []
    for i in files:
        chunk = pd.read_csv(i, sep='\t', header=0, engine='python')
        chunks.append(chunk)
    peaks = pd.concat(chunks, ignore_index=True)
    print(peaks)
    plt.figure()
    plt.hist(peaks.Position, range=[0, 2], label="unweighted")
    plt.hist(peaks.Position, range=[0, 2], weights=peaks.Prominence, label="prominence-weighted")
    plt.title("Histogram of peak position frequency")
    plt.xlabel('Position / nm')
    plt.ylabel('Counts')
    if export == 'y':
        path = path + "/frequency histogram.jpg"  # path for plots
        plt.savefig(path, format='jpg')  # save figure in jpg format
    plt.show()
    path = os.getcwd() + "/peaks list.txt"
    peaks.to_csv(path, sep="\t")
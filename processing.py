import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pybaselines
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks, peak_prominences, peak_widths
import hashlib
from pathlib import Path


def duplicate_removal(path_in, list_of_files):
    unique_files = dict()
    # Running a for loop on all the files
    for file in list_of_files:
        # Finding complete file path
        file_path = Path(os.path.join(path_in, file))
        # Converting all the content of
        # our file into md5 hash.
        hash_file = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        # If file hash has already been added we'll simply delete that file
        if hash_file not in unique_files:
            unique_files[hash_file] = file_path
        else:
            os.remove(file_path)
            print(f"{file} has been deleted")


def preproc_asls(path_in, file_input, export):
    path = path_in + "/" + file_input  # creates path to open files
    # imports file into dataframe and creates dataframe for
    spectra = pd.read_csv(path, delimiter=" ", header=13, names=["Position", "Current"], engine='python', skipfooter=1)
    # module to crop saturated currents
    maxcurrent = np.amax(spectra.Current)
    spectra = spectra[spectra.Current < maxcurrent]  # to rethink
    current = uniform_filter1d(spectra.Current, 10)  # smoothing
    baseasls = pybaselines.whittaker.asls(current, lam=10 ** 3, p=0.02)[0]  # baseline calculation with asls
    residuals = current - baseasls  # residual calculation
    residuals = residuals[spectra.Current < maxcurrent]
    spectra['Residuals'] = residuals
    spectra['Baseline'] = baseasls
    # plotting(spectra, file_input, export)
    peaks = peak_extraction(spectra)
    if export == 'y':
        exporter(path_in, file_input, spectra, peaks)
    return spectra, peaks


def preproc_derpsalsa(path_in, file_input, export, param=None):
    if param.empty is True:
        param.at[0, 'SmoothingWindow'] = 20
        param.at[0, 'Lambda'] = 2000
        param.at[0, 'p'] = 0.002
    smooth_wind = int(param.SmoothingWindow[0])
    lam = float(param.Lambda[0])
    p = float(param.p[0])
    path = path_in + "/" + file_input  # creates path to open files
    # imports file into dataframe and creates dataframe for
    spectra = pd.read_csv(path, delimiter=" ", header=13, names=["Position", "Current"], engine='python', skipfooter=1)
    # module to crop saturated currents
    maxcurrent = np.amax(spectra.Current)
    spectra = spectra[spectra.Current < maxcurrent]  # to rethink
    current = uniform_filter1d(spectra.Current, smooth_wind)  # smoothing
    basederpsalsa = pybaselines.whittaker.derpsalsa(current, lam=lam, p=p)[0]
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
    path_spectra = path_in + "/preprocessed spectra/"
    path_out = path_spectra + file_input.replace(".ts", "-spectra.txt")
    spectra.to_csv(path_out, header=True, sep="\t", index=False)
    # data export: 2)peak features
    if not peaks.empty:
        path_peaks = path_in + "/peak data/"
        path_out = path_peaks + file_input.replace(".ts", "-peaks.txt")
        peaks.to_csv(path_out, header=True, sep="\t", index=False)


#     FUNCTIONS FOR HISTOGRAM
def proc_hist(files, export="n"):
    path = os.getcwd()
    chunks = []
    for i in files:
        chunk = pd.read_csv(i, sep='\t', header=0, engine='python')
        chunks.append(chunk)
    peaks = pd.concat(chunks, ignore_index=True)
    print("In total the number of found peaks is", len(peaks))
    hist_peaks = pd.DataFrame()
    max_peak = max(peaks.Position)
    plt.figure()
    plt.hist(peaks.Position, range=[0, 2], label="unweighted", alpha=0.5)
    plt.hist(peaks.Position, range=[0, 2], weights=peaks.Prominence, label="prominence-weighted", alpha=0.5)
    plt.title("Histogram of peak position frequency")
    plt.xlabel('Position / nm')
    plt.ylabel('Counts')
    plt.legend()
    if export != 'n':
        path = path + "/frequency histogram.jpg"  # path for plots
        plt.savefig(path, format='jpg')  # save figure in jpg format
    plt.show()
    hist_peaks['counts-unweigh'] = np.histogram(peaks.Position, bins=10, range=[0, max_peak])[0]
    hist_peaks['counts-promin'] = np.histogram(peaks.Position, bins=10, range=[0, max_peak], weights=peaks.Prominence)[0]
    hist_peaks['counts-height'] = np.histogram(peaks.Position, bins=10, range=[0, max_peak], weights=peaks.Height)[0]
    bins = np.histogram(peaks.Position, bins=10, range=[0, max_peak])[1]
    hist_peaks['bins'] = bins[0:-1]
    if export != 'n':
        path = os.getcwd() + "/peaks list.txt"
        peaks.to_csv(path, sep="\t")
        path = os.getcwd() +"/histogram data.txt"
        hist_peaks.to_csv(path, sep="\t", index=False)

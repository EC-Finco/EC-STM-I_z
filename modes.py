import glob
import os
import numpy as np
import pandas as pd

import processing
import paths


def duplicates():
    extension = 'ts'
    # insert the path of the spectra
    path_in = input("Type the path of spectra: ")
    os.chdir(path_in)
    tsresult = [i for i in glob.glob('*.{}'.format(extension))]
    processing.duplicate_removal(path_in, tsresult)
def spectra_analysis():
    # importing filenames
    extension = 'ts'
    # insert the path of the spectra
    path_in = input("Type the path of spectra: ")
    os.chdir(path_in)
    new_folders = input("create new folders for code output? [y/n]\n")
    path_spectra, path_peaks = paths.folders_out(path_in, new_folders)
    export = input("Generate output files? [y/n]\n")
    # Find relevant TSs in folder
    tsresult = [i for i in glob.glob('*.{}'.format(extension))]
    print("Number of found spectra: ", len(tsresult))
    # import, baseline and export
    file_input = ' '
    mode = input("should the calculations run on a single spectra or all the ones in the folder? [one/all] ")
    if mode == 'one':
        file_input = input("Type name of file to analyze: ")
        path = path_in
        param = manual_mode()
        spectra, peaks = processing.preproc_derpsalsa(path_in, file_input, export, param)
    else:
        print("Running preprocessing on all compatible files")
        param = manual_mode()
        i = 0
        for file_input in tsresult:
            i = i + 1
            print("...", file_input, "...", "file n.", i)
            spectra, peaks = processing.preproc_derpsalsa(path_in, file_input, export, param)
    path_param = path_in + "/parameters.txt"
    param.to_csv(path_param, header=True, sep="\t", index=False)
    return path_in, export, spectra, peaks


def histogram(seq="no", par_dir="", export="n"):
    if seq == "no":
        path_in = input("Paste path of found peaks:\n")
        export = input("Should the histogram be exported?")
    else:
        path_in = par_dir + "/peak data/"
    # importing peak files
    os.chdir(path_in)
    print("The histogram data and plot will be placed in the same folder")
    path = path_in + "/*-peaks.txt"
    files = glob.glob(path, recursive=True)
    print("The peak files found in this folder are:\t", len(files))
    processing.proc_hist(files, export)


def manual_mode():
    manual_mode = input("Do you want to set parameters of the calculation? [y/n]\n")
    param = pd.DataFrame()
    if manual_mode == 'y':
        param.at[0, 'SmoothingWindow'] = input("Insert the width of the smoothing window:\t")
        param.at[0, 'Lambda'] = input("Insert the value for lambda:\t")
        param.at[0, 'p'] = input("Insert the value for p:\t")
    return param

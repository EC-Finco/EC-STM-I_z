import glob
import os
import numpy as np
import pandas as pd

import processing
import paths


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
        spectra, peaks = processing.preproc_derpsalsa(path_in, file_input, export)
    else:
        print("Running preprocessing on all compatible files")
        i = 0
        for file_input in tsresult:
            i = i + 1
            print("...", file_input, "...", "file n.", i)
            spectra, peaks = processing.preproc_derpsalsa(path_in, file_input, export)
    return path_in, export, spectra, peaks


def histogram(seq="no", par_dir="",export="y"):
    if seq == "no":
        path_in = input("Paste path of found peaks:\n")
    else:
        path_in = par_dir + "/peak data/"
    # importing peak files
    os.chdir(path_in)
    print("The histogram data and plot will be placed in the same folder")
    path = path_in + "/*-peaks.txt"
    files = glob.glob(path, recursive=True)
    print("The peak files found in this folder are:\t", len(files))
    processing.proc_hist(files, export=export)


# -----------------------------------MODULE CHECKS------------------------------

# Check for modules, try to exit gracefully if not found
import sys
import importlib
import paths
import processing
try:
    importlib.import_module('numpy')
    foundnp = True
except ImportError:
    foundnp = False
try:
    importlib.import_module('matplotlib')
    foundplot = True
except ImportError:
    foundplot = False
try:
    importlib.import_module('pandas')
    foundpd = True
except ImportError:
    foundplot = False
if not foundnp:
    print("Numpy is required. Exiting")
    sys.exit()
if not foundplot:
    print("Matplotlib is required. Exiting")
    sys.exit()
if not foundpd:
    print("Pandas is required. Exiting")
    sys.exit()
try:
    importlib.import_module('pybaselines')
    foundbase = True
except ImportError:
    foundbase = False
if not foundbase:
    print("Pybaselines is required. Exiting")
    sys.exit()
# -------------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pybaselines
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks, peak_prominences, peak_widths
# -------------------------------------------------------------------------------

import os
import glob

# Stop message from appearing
import warnings

warnings.filterwarnings("ignore", ".*GUI is implemented.*")
warnings.filterwarnings("ignore", ".*No labelled objects found.*")

# importing filenames
extension = 'ts'
# insert the path of the spectra
path_in = input("Type the path of spectra: ")
os.chdir(path_in)
new_folders = input("create new folders for code output? [y/n]")
path_spectra, path_peaks = paths.folders_out(path_in, new_folders)

# Find relevant TSs in folder
tsresult = [i for i in glob.glob('*.{}'.format(extension))]
print("Number of found spectra: ", len(tsresult))
# import, baseline and export
file_input = ' '
mode = input("should the calculations run on a single spectra or all the ones in the folder? [one/all]")
if mode == 'one':
    file_input = input("Type name of file to analyze:")
    path = path_in
    spectra, peaks = processing.preproc(path_in, file_input)
else:
    print("Running preprocessing on all compatible files")
    for file_input in tsresult:
        path = path_in
        print("...", file_input, "...")
        spectra, peaks = processing.preproc(path_in, file_input)


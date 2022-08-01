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
import quo

# Stop message from appearing
import warnings
import modes
warnings.filterwarnings("ignore", ".*GUI is implemented.*")
warnings.filterwarnings("ignore", ".*No labelled objects found.*")

mode = input("Choose calculation method: D=Duplicate removal S=Spectra analysis - H=Histogram plot - B=Both \n")
if mode == 'D':
    modes.duplicates()
elif mode == 'S':
    modes.spectra_analysis()
elif mode == 'H':
    modes.histogram()
elif mode == 'B':
    path_in = modes.spectra_analysis()[0]
    export = input("Should the histogram be exported?")
    seq = "yes"
    modes.histogram(seq, path_in, export)

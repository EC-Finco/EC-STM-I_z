# -----------------------------------MODULE CHECKS------------------------------

# Check for modules, try to exit gracefully if not found
import sys
import importlib

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
path_in = input("Type the path of spectra: ")
os.chdir(path_in)
file_input = input("Type name of file to analyze: ")
path = path_in + "/" + file_input  # creates path to open files
# imports file into dataframe and creates dataframe for
spectra = pd.read_csv(path, delimiter=" ", header=13, names=["Position", "Current"], engine='python', skipfooter=1)
peaks = pd.DataFrame()
# module to crop saturated currents
maxcurrent = np.amax(spectra.Current)
spectra = spectra[spectra.Current < maxcurrent]  # to rethink
current = uniform_filter1d(spectra.Current, 10)  # smoothing
basepen_poly = pybaselines.polynomial.penalized_poly(current, spectra.Position)[0]
basederp = pybaselines.whittaker.derpsalsa(current, lam=2*10**3, p=0.0005)[0]
baseimod3 = pybaselines.polynomial.imodpoly(current, spectra.Position, poly_order=3)[0]  # baseline calculation with imodpoly
residualderp = current - basederp  # residual calculation
residualimod3 = current - baseimod3
spectra['Residuals'] = residualimod3
residualpen_poly = current - basepen_poly
# peak finding
peak, params = find_peaks(residualimod3, prominence=0.5)  # collect the indices of peaks with a minimum prominence of 0.2
peakpos = spectra.Position[peak]
print(params)
# peak validation
prominences = peak_prominences(residualimod3, peak)[0]
widths = peak_widths(residualimod3, peak)[0]  # width in number of points
density = np.amax(spectra.Position) / len(spectra.Position)
widths = widths * density  # width in nm
heights = peak_widths(residualimod3, peak)[1]
peaks['Position (nm)'] = peakpos
peaks['Prominence'] = np.transpose(prominences)
peaks['Width (nm)'] = np.transpose(widths)
peaks['Height (nA)'] = np.transpose(heights)
plt.figure()
plt.plot(spectra.Position, spectra.Current)
plt.plot(spectra.Position, residualimod3, label="res-imod3")
plt.plot(spectra.Position, residualderp, label="res-derp")
plt.plot(spectra.Position, residualpen_poly, label="res-pen_poly")
plt.plot(spectra.Position, baseimod3, label="imod3")
plt.plot(spectra.Position, basederp, label="derp lam=4E3, p=0.001")
plt.plot(spectra.Position, basepen_poly, label="pen_poly")
plt.plot(peakpos, residualimod3[peak], "x")
plt.legend()
plt.title(file_input)
plt.xlabel('Position / nm')
plt.ylabel('Current / nA')
plt.show()


#-----------------------------------MODULE CHECKS------------------------------

# Check for modules, try to exit gracefully if not found
import sys
import importlib

import pybaselines

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

#-------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import math
from pybaselines.whittaker import asls
#-------------------------------------------------------------------------------

import os
import glob

# Stop message from appearing
import warnings
warnings.filterwarnings("ignore",".*GUI is implemented.*")
warnings.filterwarnings("ignore",".*No labelled objects found.*")

#importing filenames
extension = 'ts'
#insert the path of the spectra
path=input("Type the path of spectra: ")
os.chdir(path)
#uncomment to check that cwd is the wanted one
#path = os.getcwd()
#print("The targeted path is", path)
#Find relevant TSs in folder
tsresult = [i for i in glob.glob('*.{}'.format(extension))]
#uncomment to Verify the content of tsresult
#print("Plotting the following:")
#print(tsresult)

#import, baseline and export
k=0
#while k < len(tsresult):
path = os.getcwd()
path = path + "/" + tsresult[1]
spectra=pd.read_csv(path, delimiter=" ",header=13, names=["Position","Current"],engine='python', skipfooter=1)
baseline=pybaselines.whittaker.asls(spectra.Current)



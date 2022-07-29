import os


def folders_out(path_in, new_folders):
    path_spectra = path_in + "/preprocessed spectra/"
    path_peaks = path_in + "/peak data/"
    path_plots = path_in + "/plots/"
    if new_folders == "y":
        os.mkdir(path_spectra)
        os.mkdir(path_peaks)
        os.mkdir(path_plots)
    return path_spectra, path_peaks

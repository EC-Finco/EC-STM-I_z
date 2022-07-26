import os


def folders_out(path_in, new_folders):
    if new_folders == "y":
        path_spectra = path_in + "/preprocessed spectra/"
        path_peaks = path_in + "/peak data/"
        os.mkdir(path_spectra)
        os.mkdir(path_peaks)
    else:
        path_spectra = path_in + "/preprocessed spectra/"
        path_peaks = path_in + "/peak data/"
    return path_spectra, path_peaks

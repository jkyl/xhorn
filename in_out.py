import h5py

def write_to_hdf5(f, array, metadict):
    '''
    Inputs:
        "filename.hdf5", np.ndarray, and metadata dictionary that must contain "utc_time",
        "angle_degs", and "samp_rate_mhz" keys. 

    Outputs:
        Writes to an .hdf5 file whose dataset names correspond to utc times. The datasets 
        contain numpy arrays of spectra, and also attributes passed via the metadict variable. 
    '''
    d = f.create_dataset(str(metadict['utc_time']), data = array)
    for key, val in metadict.items():
        d.attrs.create(key, val)

def read_from_hdf5(fname):
    '''
    Inputs:
        .hdf5 file path
    Outputs:
        Dictionary of data organized by utc time, where each point contains a numpy array of a 
        spectrum and any metadata like angle, sample rate, and time (more can be added). 
    '''
    f = h5py.File(fname, 'r')
    d = {}
    for key, val in f.items():
        key = str(key)
        d[key] = {}
        d[key]['spec'] = val[:]
        for k, v in val.attrs.items():
            d[key][str(k)] = v
    f.close()
    return d

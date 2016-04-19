import h5py, os
from datetime import datetime
import time_sync as ts
import numpy as np

def write_to_hdf5(fname, array, metadict):
    '''
    Inputs:
        "filename.hdf5", np.ndarray, and metadata dictionary that must contain "utc_time",
        "angle_degs", and "samp_rate_mhz" keys. 

    Outputs:
        Writes to an .hdf5 file whose dataset names correspond to utc times. The datasets 
        contain numpy arrays of spectra, and also attributes passed via the metadict variable. 
    '''
    f = h5py.File(fname)
    d = f.create_dataset(str(metadict['utc']), data = array)
    for key, val in metadict.items():
        d.attrs.create(key, val)
    f.close()

def read_to_dict(fname):
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

def read_to_arrays(fnames):
    '''
    '''
    data = {'spec': []}
    if len(fnames) != 0:
        for f in list(fnames):
            f = h5py.File(f, 'r')
            for val in f.values():
                data['spec'].append(val[:])
                for k, v in f[val].attrs():
                    if not k in data:
                        data[k] = []
                    data[k].append(v)
        return {k: np.vstack(v) for k, v in data.items()}
    else:
        raise IOError
    
def read_time_range(dt_0 = None, dt_f = None):
    '''
    Takes two tuples which are converted to datetime objects, and reads in all 
    data within that range to numpy arrays. 
    '''
    if dt_0 is None:
        dt_0 = (1970, 1, 1)
    if dt_f is None:
        dt_f = (3000, 1, 1)
    dt_0, dt_f = (ts.dt_to_epoch(datetime(*i)) for i in (dt_0, dt_f))
    inrange = []
    for i in os.listdir('output'):
        if '.h5' in i:
            epoch = ts.iso_to_epoch(i[:-3])
            if dt_0 <= epoch <= dt_f:
                inrange.append('output/'+i)
    try:
        return read_to_arrays(sorted(inrange))
    except IOError:
        raise IOError, 'No data in the provided range.'
    
    
    
    
    
    

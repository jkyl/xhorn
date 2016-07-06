import h5py, os
from datetime import datetime
import time_sync as ts
import numpy as np
import glob

def write_to_hdf5(fname, array, metadict):
    '''
    Inputs:
        "filename.h5", np.ndarray, and metadata dictionary.

    Outputs:
        Writes to an .hdf5 file whose dataset names correspond to utc times. The datasets 
        contain numpy arrays of spectra, and also attributes passed via the metadict variable. 
    '''
    f = h5py.File(fname)
    d = f.create_dataset(str(metadict['utc']), data = array)
    for key, val in metadict.items():
        d.attrs.create(key, val)
    f.close()

def read_to_arrays(fnames):
    '''
    Reads a file or list of files into arrays stored in a dictionary whose keys 
    correspond to the measured quantities. 
    '''
    data = {'spec': []}
    if type(fnames) == str:
        fnames = [fnames]    
    if len(fnames) != 0:
        for f in fnames:
            print(f)
            f = h5py.File(f, 'r')
            for val in f.values():
                data['spec'].append(val[:])
                for k, v in val.attrs.items():
                    if not k in data:
                        data[str(k)] = []
                    data[k].append(v)
            f.close()
        return {k: np.vstack(v) for k, v in data.items()}
    else:
        raise IOError, 'Filename not provided'
    
def read_time_range(dt_0 = None, dt_f = None, ext=None):
    '''
    Takes two tuples which are converted to datetime objects, and reads in all 
    data within that range to numpy arrays. 
    '''
    if dt_0 is None:
        dt_0 = (1970, 1, 1)
    if dt_f is None:
        dt_f = (3000, 1, 1)
    if ext is None:
        ext=['[0-9]','_scan']
    if type(ext) == str:
        ext = [ext]
    epoch_0, epoch_f = (ts.dt_to_epoch(datetime(*i)) for i in (dt_0, dt_f))
    inrange = []
    path = '/'.join(os.path.abspath(ts.__file__).split('/')[:-2]) + '/output/'
    fn = []
    for k, val in enumerate(ext):
        fn0 = glob.glob(path + '*' + val + '.h5')
        fn = fn + fn0
    for i in fn:
        if '.h5' in i:
            isotime = os.path.basename(\
                '.'.join(i.split('.')[:-1]).split('_')[0])
            epoch = ts.iso_to_epoch(isotime)
            if epoch_0 <= epoch <= epoch_f:
                inrange.append(i)
    try:
        return read_to_arrays(sorted(inrange))
    except IOError:
        raise 

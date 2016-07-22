import numpy as np
import os
from tqdm import trange
from datetime import datetime

def saver(s, path=None):
    '''
    Snaps and saves a spectrum to an .npz file with the specified path. 
    '''
    if path is None:
        path = '/'.join(os.path.abspath(__file__).split('/')[:-2]\
        + ['lab_spec_data/{}']).format(datetime.now().isoformat()[:-7])
    np.savez_compressed(path, s.snap_spec(),
                        **{k: v for k, v in s.__dict__.items() if k!= '_roach'})

def scanner(s, nscan=10):
    '''
    Loops with a progress bar over nscans, taking spectra and saving with saver().
    Filenames are local time isoformatted strings. 
    '''
    for i in trange(nscan):
        saver(s)

def loader(path):
    '''
    Returns a (spec, metadata) tuple when given a valid .npz filepath.
    '''
    d = {k: v for k, v in np.load(path).iteritems()}
    return d.pop('arr_0'), {k: v.item() for k, v in d.items()}
        
        
        

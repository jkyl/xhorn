import numpy as np
import os
import time
from tqdm import trange
from datetime import datetime
from sig_gen import Gen

def integrate(s, int_time=10, LO_freq=9.5, LO_time=None, fname=None):
    '''
    Integrates for the specified interval in seconds and saves to path. 
    ''' 
    #Calculate number of integrations
    n_ints = int(round(float(int_time)/s.acc_len))
    assert(n_ints>0)

    #Determine LO switching
    specs = np.zeros((n_ints, 2048))
    times = np.zeros(n_ints)
    t0 = time.time()
    if not LO_freq is None:
        g = Gen()
        g.set_pow(10) #10 dBm output power
        g.set_rf(True) #Turn on

        #Create array of LO frequencies over time
        if type(LO_freq) in (float, int):
            LO_freq = np.array([LO_freq] * n_ints)
            
        elif (type(LO_time) in (float, int)) and hasattr(LO_freq, '__iter__'):
            LO_freq = np.array(LO_freq)
            n_at_each = int(round(float(LO_time)/s.acc_len))
            assert(n_at_each>0)
            LO_freq = np.tile(np.repeat(LO_freq, n_at_each),
                              int(round(float(n_ints / n_at_each))))[:n_ints]

        #Snap and stack spectra
        for i in trange(n_ints):
            if i==0 or (LO_freq[i-1] != LO_freq[i]):
                g.set_freq(LO_freq[i])
                time.sleep(s.acc_len)
            specs[i] = s.snap_spec()
            times[i] = time.time() - t0
    else:
        for i in trange(n_ints):
            specs[i] = s.snap_spec()
            times[i] = time.time() - t0
        
    #Find absolute path to data dir and save
    if fname is None:
        fname = '/'.join(os.path.abspath(__file__).split('/')[:-2]\
        + ['lab_spec_data/{}']).format(datetime.now().isoformat()[:-7])
    np.savez_compressed(fname, spec=specs, LO_freq=LO_freq, time=times,
                        **{k: v for k, v in s.__dict__.items() if k!= '_roach'})
        

def loader(fname):
    '''
    Returns: when given a valid .npz filename.
    spec
    LO_freq
    time
    metadata
    '''
    d = {k: v for k, v in np.load(fname).iteritems()}
    return d.pop('spec'), d.pop('LO_freq'), d.pop('time'), {k: v.item() for k, v in d.items()}
        
        
        

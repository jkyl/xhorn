from xhorn import reduc_spec
from numpy import *
from matplotlib.pyplot import *
from IPython.core.debugger import Tracer; debug_here = Tracer()

def get_data(ti=(2016,6,28), tf=(2016, 6, 29)):
    '''
    Thin wrapper for reduc_spec.data. No need to call d.reduce().
    '''
    return reduc_spec.data(ti, tf)

def reduce(d, za0_ind = -1):
    '''
    Loops over each scan to calculate each za's spec's deviation 
    from the mean over all za's specs, proportional to a given 
    za's spec's deviation from the mean spec. Populates an (nscan
    x nchannel x nza) array with the results. Also calculcates the 
    expectation value for this quantity based on airmass alone. 
    '''
    scan_inds = d.getscanind()
    za = unique(d.za[scan_inds])
    rv = zeros((d.nscan, d.nf, za.size))
    am = d.za2am(za)
    mean_am = d.am[scan_inds].mean()
    za0 = za[za0_ind]
    am0 = am[za0_ind]
    for i, za1 in enumerate(za):
        am1 = am[where(za==za1)]
        for k in range(d.nscan):
            za1_inds = where((d.scan==k) & (d.za==za1))[0]
            za0_inds = where((d.scan==k) & (d.za==za0))[0]
            mean_spec = d.spec[d.getscanind(k)].mean(0)
            za1_spec = d.spec[za1_inds].mean(0)
            za0_spec = d.spec[za0_inds].mean(0)
            dif_ratio = (za1_spec - mean_spec) / (za0_spec - mean_spec)
            rv[k, :, i] = dif_ratio
    expect = (am - mean_am) / (am0 - mean_am)
    return rv, expect

def save_data(data, expect, fname='../reduc_data/test'):
    '''
    Saves the data cube and expectation values in a compressed .npz 
    format.
    '''
    savez_compressed(fname, data=data, expect=expect)

def load_data(fname='../reduc_data/test.npz'):
    '''
    Loads the data cube and expectation values from an .npz file in 
    xhorn/reduc_data/.
    '''
    with load(fname) as f:
        data = f['data']
        expect = f['expect']
    return data, expect

def weighted_mean(data, start=700, stop=1600, weight_power=-1):
    '''
    Calculcates a weighted mean over scans based on the sigma in
    the given range of channels.
    '''
    weights = data.copy()[:, start:stop, :]
    weights = nanstd(weights, axis=1)**weight_power
    weights = tile(weights, (data.shape[1], 1, 1)).swapaxes(1, 0)
    return array(ma.average(data.copy(), axis=0, weights=weights))

def mean_res(avgd_data, expect):
    '''
    Calculates the residuals between an averaged bunch of data
    and a prediction. 
    '''
    return nanmean(avgd_data.copy() - tile(expect, (avgd_data.shape[0], 1)), 0)

def plot_data(lines, expect):
    '''
    Accepts an (n_chans, n_zas)-shaped array of reduced data, and 
    an (n_zas,)-shaped array of expectations, and plots them as 
    (n_zas) populations alongside the corresponding prediction. 
    '''
    #gca().set_color_cycle(None)
    plot(lines, '.')
    gca().set_color_cycle(None)
    plot([0, lines.shape[0]], tile(expect, (2, 1)))
    ylim(-1.5, 1.5)
    xlim(300, 2000)
    grid(True)
    
def waterfall_res(data, expect):
    close('all')
    for index, prediction in enumerate(expect):
        figure(index + 1)
        img = data[:, :, index].copy() - prediction
        imshow(img)
        clim(-2, 2)
        colorbar()


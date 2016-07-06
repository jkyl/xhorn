from xhorn import reduc_spec
from numpy import *
from matplotlib.pyplot import *
from IPython.core.debugger import Tracer; debug_here = Tracer()
from xhorn import time_sync as ts
from scipy.stats import sem

def get_data(ti=(2016,6,28), tf=(2016, 6, 29)):
    '''
    Thin wrapper for reduc_spec.data. No need to call d.reduce().
    '''
    return reduc_spec.data(ti, tf)

def reduce(d, za0_ind = 0):
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
    n_per_scan = d.mjd.size / d.nscan
    times = vectorize(ts.mjd_to_iso)(d.mjd)[::n_per_scan]
    return rv, expect, times

def save_data(data, expect, times, fname='../reduc_data/test'):
    '''
    Saves the data cube and expectation values in a compressed .npz 
    format.
    '''
    savez_compressed(fname, data=data, expect=expect, times=times)

def load_data(fname='../reduc_data/test.npz'):
    '''
    Loads the data cube and expectation values from an .npz file in 
    xhorn/reduc_data/.
    '''
    with load(fname) as f:
        data = f['data']
        expect = f['expect']
        times = f['times']
    return data, expect, times
    
def sigma(data, axis):
    return nanstd(data.copy(), axis=axis)
    
def mu(data, axis, weights=None):
    if weights is None:
        weights = ones_like(data)
    return array(ma.average(data.copy(), axis=axis, weights=weights))
    
def mean_res(avg_data, expect):
    '''
    Calculates the residuals between some averaged, reduced data
    and a prediction. 
    '''
    return nanmean(avg_data.copy() - tile(expect, (avg_data.shape[0], 1)), 0)

def am_err(za, d_za):
    d_cos = d_za * sin(pi * za / 180)
    percent_err = d_cos * pi / (180 * cos(pi * za / 180))
    return percent_err / cos(pi * za / 180)
    
def ratio_err(za, d_za, za_0_ind = 0):
    am = 1 / cos(pi * za / 180)
    d_am = am_err(za, d_za)
    mean_am = am.mean()
    d_mean_am = mean_am * sqrt(((d_am / am)**2).sum())
    ratio = (am - mean_am) / (am[za_0_ind] - mean_am)
    d_ratio = ratio * sqrt((d_am/am)**2 + 2*((d_mean_am / mean_am)**2)\
                          +(d_am[za_0_ind] / am[za_0_ind])**2)
    return abs(d_ratio)
    
def plot_data(data, expect):
    '''
    Accepts an (n_chans, n_ZAs)-shaped array of reduced data, and 
    an (n_ZAs,)-shaped array of expectations, and plots them as 
    (n_ZAs) populations alongside the corresponding prediction. 
    '''
    zas = array([20., 32.6, 40.24, 45.74, 50.])
    d_za = 1 #deg
    za_0_ind = 0
    colors = ['b', 'g', 'r', 'c', 'm']
    f = linspace(9.5, 11.7, 2048)
    ex = tile(expect, (2, 1))
    d_ex = tile(ratio_err(zas, d_za, za_0_ind), (2, 1))
    figure(1, figsize=(15, 8));clf()
    plot([],[], 'k', label='Expectation values')
    plot([], [], 'k.', label='Mean')
    plot([], [], 'gray', linewidth=10, label='$\sigma_{za}=\pm1^\circ$')
    for i in range(data.shape[2]):
        c = colors[i]
        mean_ = mu(data, 0)[:,i]
        err = sigma(data, 0)[:,i]
        fill_between(f, mean_ - err, mean_ + err,
                     facecolor=c, edgecolor=c, alpha=0.8)
        fill_between([f[0], f[-1]], ex[:,i] - d_ex[:,i], ex[:,i] + d_ex[:,i],
                     facecolor = 'gray', edgecolor='gray', alpha=.5)
        plot([],[],c,label = 'za={}$^\circ \pm 1\sigma$'.format(zas[i]), 
             linewidth=10)
        plot(f, mu(data, 0)[:, i], 'k.', ms=.8)
        plot([f[0], f[-1]], [expect[i], expect[i]], 'k')
    ylim(-1.5, 1.5)
    xlim(9.75, 11.5)
    grid(True)
    legend(loc='upper left',prop={'size':11})
    title(r'$T_{sky}$ ratio, 5 airmasses with 1 sigma error bands, ca. 30 hours of scanning')
    xlabel('Frequency (GHz)')
    ylabel(r'$\frac{V^{\,2}(\theta_z)-\overline{V^{\,2}}}{V^{\,2}(\theta_z=%i^\circ)-\overline{V^{\,2}}}\,$ , average over 600 scans'%(zas[za_0_ind]), 
           size=16)
    tight_layout()
    
def waterfall_res(data, expect, times, dosave=False):
    '''
    Generates (n_ZA) images of the residuals of the reduced data
    wrt. their expectation over time. 
    '''
    close('all')
    zas = array([20., 32.6, 40.24, 45.74, 50.])
    for index, prediction in enumerate(expect):
        fig, ax1 = subplots(figsize=(10, 10))
        img = data[:, :, index].copy() - prediction
        imshow(img, vmin=-1, vmax=1)
        #colorbar()
        xticks(arange(2048)[::256], 
               [round(a, 2) for a in linspace(9.5, 11.7, 2048)[::256]],
               rotation=-45, ha='left')
        xlabel('Frequency (GHz)')
        ylabel('Scan number')
        ax2 = ax1.twinx()
        yticks(arange(times.size)[::-50], 
               [t[6:-7] for t in times[::50]], 
               size='x-small', va='top', rotation=-45)
        ylabel('Time (UTC)')
        title(r'$T_{{sky}}$ ratio residuals, railed at $\pm1$, $\theta_z={}^\circ$'.format(zas[index]))
        tight_layout()
        if dosave:
            savefig('../reduc_data/waterfall_{}.png'.format(index))


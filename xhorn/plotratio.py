from xhorn import reduc_spec
from numpy import *
from matplotlib.pyplot import *
from IPython.core.debugger import Tracer; debug_here = Tracer()

def get_data(ti=(2016,6,28), tf=(2016, 6, 29), want_cal=False):
    d=reduc_spec.data(ti, tf)
    d.reduc()
    return d

def go(d, za0_ind = -1):
    scan_inds = d.getscanind()
    za = unique(d.za[scan_inds])
    rv = zeros((d.nscan, d.nf, za.size))
    am = d.za2am(za)
    mean_am = d.am[scan_inds].mean()
    za0 = za[za0_ind]
    am0 = am[za0_ind]
    for i, a in enumerate(za):
        za1 = a
        am1 = am[where(za==za1)]
        for k in range(d.nscan):
            za_1_inds = where((d.scan==k) & (d.za==za1))[0]
            za_0_inds = where((d.scan==k) & (d.za==za0))[0]
            mean_spec = d.spec[d.getscanind(k)].mean(0)
            za_1_spec = d.spec[za_1_inds].mean(0)
            za_0_spec = d.spec[za_0_inds].mean(0)
            dif_ratio = (za_1_spec - mean_spec) / (za_0_spec - mean_spec)
            rv[k, :, i] = dif_ratio
    expect = (am - mean_am) / (am0 - mean_am)
    return rv, expect

def plot_rv(rv, expect):
    gca().set_color_cycle(None)
    plot(rv.mean(0), '.')
    gca().set_color_cycle(None)
    plot([0, rv.shape[1]], tile(expect, (2, 1)))
    ylim(-5, 5)
    xlim(300, 2000)
   
def waterfall(rv, expect):
    close('all')
    for index, prediction in enumerate(expect):
        figure(index + 1)
        img = rv[:, :, index].copy() - prediction
        imshow(img)
        clim(-2, 2)
        

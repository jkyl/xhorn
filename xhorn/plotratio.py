from xhorn import reduc_spec
from numpy import *
from matplotlib.pyplot import *
from IPython.core.debugger import Tracer; debug_here = Tracer()

def get_data(ti = (2016,6,24), tf = (2016,6,25)):
    d=reduc_spec.data(ti, tf)
    d.reduc()
    return d

def go(d):
    scan_inds = d.getscanind()
    za = unique(d.za[scan_inds])
    rv = zeros((d.nscan, d.nf, za.size))
    am = d.za2am(za)
    mean_am = d.am[scan_inds].mean()
    za0 = za[4]#                 <--- choose airmasses here
    am0 = am[where(za==za0)]
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
    legend()
   
def waterfall(rv, expect):
    for index, prediction in enumerate(expect):
        figure(index + 1)
        img = rv[:, :, index].copy() - prediction
        #img[isnan(img)] = 0
        imshow(img)
        clim(-1, 1)
        

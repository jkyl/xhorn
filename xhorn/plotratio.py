from xhorn import reduc_spec
from numpy import *
from matplotlib.pyplot import *
from IPython.core.debugger import Tracer; debug_here = Tracer()

def get_data(ti = (2016,6,24), tf = (2016,6,25)):
    d=reduc_spec.data(ti, tf)
    d.reduc()
    return d

def go(d, doplot=False):
    scan_inds = d.getscanind()
    za = unique(d.za[scan_inds])
    colors = ['b', 'g', 'r', 'c', 'orange']
    clf()
    rv = {}
    for i, a in enumerate(za):
        za1 = za[0]#                 <--- choose airmasses here
        za2 = a
        am = d.za2am(za)
        am1 = am[where(za==za1)]
        am2 = am[where(za==za2)]
        mean_am = d.am[scan_inds].mean()
        for k in range(d.nscan):
            za_1_inds = where((d.scan==k) & (d.za==za1))[0]
            za_2_inds = where((d.scan==k) & (d.za==za2))[0]
            mean_spec = d.spec[d.getscanind(k)].mean(0)
            za_1_spec = d.spec[za_1_inds].mean(0)
            za_2_spec = d.spec[za_2_inds].mean(0)
            dif_ratio = (za_1_spec - mean_spec) / (za_2_spec - mean_spec)
            try:
                rv[a].append(dif_ratio)
            except KeyError:
                rv[a] = []
                rv[a].append(dif_ratio)
        v = array(rv[a]).mean(axis=0)
        rv[a] = v
        if doplot:
            plot(v, '.', color = colors[i], label = 'za = {}'.format(a))
            plot([0,2048], tile((am1 - mean_am) / (am2 - mean_am), (2)), color = colors[i])
            ylim(-5, 5)
            xlim(300, 2000)
            legend()
    return rv


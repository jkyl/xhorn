from numpy import *
from matplotlib.pyplot import *
from sig_gen import Gen
import time

F_AXIS = linspace(9.5, 11.7, 2048)

def reflect_spec(s, freq=10, n_accs=None):
    '''
    '''
    g = Gen()
    ion()
    g.set_freq(freq)
    g.set_pow(-40)
    g.set_rf(0)
    n = 1
    while True:
        clf()
        g.set_rf(1)
        time.sleep(s.acc_len)
        on = s.snap_spec()
        g.set_rf(0)
        time.sleep(s.acc_len)
        off = s.snap_spec()
        diffr = on - off
        diffr[1024] = 0
        plot(F_AXIS, diffr)
        xlim(freq-.2, freq+.2)
        ylim(0, 1e11 * s.acc_len)
        pause(.05)
        if n == n_accs:
            break
        n += 1

def reflect_time(s, freq=10, power=-50, n_accs=None):
    '''
    '''
    ion()
    g = Gen()
    g.set_freq(freq)
    g.set_pow(power)
    g.set_rf(0)
    n = 1; t = []; p = []
    while True:
        try:
            clf()
            g.set_rf(1)
            time.sleep(s.acc_len)
            on = s.snap_spec()
            g.set_rf(0)
            time.sleep(s.acc_len)
            off = s.snap_spec()
            diffr = on - off
            diffr[1024] = 0
            band = argmin(abs(F_AXIS - freq))
            band = [band-1, band, band+1]
            t.append(n)
            p.append(diffr[band].sum())
            semilogy(t, p, 'bo-', linewidth=3, markersize=20)
            srt, stp = xlim(max(0, n-8), max(9, n+1))
            xticks(arange(srt, stp+1))
            #bot, top = ylim(0, 5e11 * s.acc_len)
            #yticks(linspace(bot, top, 11))
            grid(True)
            tight_layout()
            ylim(1e5,1e14)
            pause(.05)
        except KeyboardInterrupt:
            return p
        if n == n_accs:
            return p
        n += 1

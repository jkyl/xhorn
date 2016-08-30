import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

FNAME = 'data/princeton.tsv'
POINT_POS = np.linspace(0, 90, 7)
FREQ_RANGE = np.linspace(.5, 4., 1000) #GHz
BASE_FREQ = 2. #GHz, the frequency for which the beam profile is exact.
TEMP = 5000. #K


def unpack(fname):
    x, y = np.loadtxt(fname, unpack = True, skiprows = 1, usecols = [0, 1])
    return x, 10.**(y/10.)


def scaled_fxn(x, y, scale):
    return interp1d(x / scale, y) # higher freq->shorter wl->narrower profile


def get_spectrum(x, y, point_pos, freq_range):
    rv = np.array([])
    for f in freq_range:
        scale = f / BASE_FREQ
        fxn = scaled_fxn(x, y, scale)
        rv = np.append(rv, float(fxn(point_pos))) 
    return freq_range, rv


def planck(x):
    f = x * (10**9) #Hz
    H = 6.626 * (10**-34) #J*s
    C = 2.998 * (10**8) #m/s
    K = 1.381 * (10**-23) #J/K
    return 2 * H * (f**3) * (C**-2) * (np.exp(H * f / (K * TEMP)) - 1)**-1
    

def spectrum_plot(x, y, pos, freq_range, weight_fxn = None):
    i, j = get_spectrum(x, y, pos, freq_range)
    ylabel = 'Response (dB)'
    if not weight_fxn is None:
        j = weight_fxn(i) * j
        ylabel = 'Intensity $(W \cdot m^{-2} \cdot sr^{-1} \cdot Hz^{-1})$'
    plt.loglog(i, j, linewidth = 2, label = r'$\theta\/=\/%s^o$'%int(pos))
    plt.legend(loc = 'best')
    plt.xlabel(r'Frequency $(Hz)$')
    plt.ylabel(r''+ylabel)
    plt.xlim(i.min(), i.max())
    plt.grid(True, which = 'both')
    plt.title(r'Spectra imparted by point sources $\theta^o$off-axis')
    plt.show()
    
    
if __name__ == '__main__':
    x, y = unpack(FNAME)
    plt.clf()
    for pos in POINT_POS:
        spectrum_plot(x, y, pos, FREQ_RANGE, planck)
    
        

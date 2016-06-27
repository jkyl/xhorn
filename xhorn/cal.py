import in_out as io
import numpy as np

def mask(angles):
    '''
    '''
    unique = np.unique(angles)
    wheres = []
    for angle in unique:
        inds = np.where(angles==angle)[0]
        wheres.append(np.array_split(inds, np.where(np.diff(inds) != 1)[0] + 1))
    return zip(unique, wheres)

def planck(f, T):
    h = 6.62606957e-34
    c = 2.99792458e8
    k = 1.3806488e-23
    x = 8 * h * np.pi / c**3
    y = f**3
    ex = np.exp(h * f / (k * T)) - 1
    return x * y / ex
    
def tsys(f, cal, sky0, sky1, a0, a1, T=290):
    '''
    '''
    am0, am1 = (1 / np.cos(np.pi * a / 180) for a in (a0, a1))
    r_cal = sky1 / cal
    r_sky = sky1 / sky0
    t_cal = planck(f, T)
    return (r_cal*t_cal / (r_cal - 1)) / (((r_sky*am1 - am1) / (am1 - r_sky*am0)) -1)

def tsky(f, cal, sky0, sky1, a0, a1, T=290):
    r_cal = sky1 / cal
    t_cal = planck(f, T)
    t_sys = tsys(f, cal, sky0, sky1, a0, a1, T)
    return r_cal*(t_cal + t_sys) - t_sys

class data:
    def __init__(self, ti=None, tf=None):
        '''
        '''
        self.d = io.read_time_range(ti, tf)
        self.a = self.d['angle_degs'].ravel()
        self.s = self.d['spec']
        self.m = mask(self.a)
        self.cal_ind = self.m[0]
        self.sky_ind = self.m[1:]
        if self.cal_ind[0] >= 0:
            self.cal_ind = []
            self.sky_ind = self.m
        self.cal_specs = []
        self.cal_means = []
        for inds in self.cal_ind[1]:
            self.cal_specs.append(self.s[inds])
            self.cal_means.append(self.s[inds].mean(axis=0))
        self.sky_specs = {}
        self.sky_means = {}
        for ang in self.sky_ind:
            s, m = [], []
            for inds in ang[1]:
                s.append(self.s[inds])
                m.append(self.s[inds].mean(axis=0))
            self.sky_specs[ang[0]] = s
            self.sky_means[ang[0]] = m
        self.lo = 9.5e9 #Hz
        
    @property
    def f(self):
        return np.linspace(0, 2.2e9, 2048) + self.lo


        

    

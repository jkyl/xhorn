import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from in_out import read_to_arrays
from scipy.stats import linregress
from decimal import *


def power_spectrum_avg():
    plt.figure(1)
    plt.clf()
    for key, val in avgs.items():
        plt.semilogy(freq, val, label = key, color=colors[key])
    plt.legend()
    plt.grid(which = 'both')
    plt.xlim(0, 2200)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power (V$^2$ /s /Hz)')
    plt.title('Averaged power spectra, {}x {}-second integrations'.format(N, acc_len))
    if dosave:
        plt.savefig('output/plots/power_spectrum_avg.pdf', format = 'pdf')
    
def power_spectrum_all():
    handles = []
    plt.figure(2)
    plt.clf()
    for key, val in data.items():
        color = colors[key]
        handles.append(mlines.Line2D([], [], color=color, label=key))
        for s in spec[key]:
            plt.semilogy(freq, s, color = color, linewidth = 0.15)
    plt.legend(handles = handles)
    plt.grid(which = 'both')
    plt.xlim(0, 2200)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power (V$^2$ /s /Hz)')
    plt.title('Individual power spectra, {}x {}-second integrations'.format(N, acc_len))
    if dosave:
        plt.savefig('output/plots/power_spectrum_all.pdf', format = 'pdf')
    
def sigma_over_mu():
    plt.figure(3)
    plt.clf()
    for key, val in avgs.items():
        plt.semilogy(freq, stds[key]/val, label = key, color = colors[key])
    plt.legend()
    plt.grid(which = 'both')
    plt.xlim(0, 2200)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('$\sigma / \mu$')
    plt.title('Standard deviation divided by mean, {}x {}-second integrations'\
              .format(N, acc_len))
    if dosave:
        plt.savefig('output/plots/sigma_over_mu.pdf', format = 'pdf')
    
def tsys_integrated():
    plt.figure(4)
    plt.clf()
    x = np.linspace(0, 300, 2)
    plt.plot(x, (slope*x) + intercept,
             label = '\n'.join(['$P=gT+P_0$',
                                '$g={:.3}\,\mathrm{{(V^2/s/Hz/K)}}$',
                                '$P_0={:.3}\,\mathrm{{(V^2/s/Hz)}}$',
                                '$T_{{sys}}={}\,\mathrm{{(K)}}$'
             ]).format(slope, intercept, int(round(intercept/slope))))
    for key, val in itgl.items():
        plt.plot(temp[key], val, 'o', markersize = 8, label = key)
    plt.legend(loc='best', numpoints=1)
    plt.grid(True)
    plt.xlabel('Temperature (K)')
    plt.ylabel(r'Power (V$^2$ /s /Hz)')
    plt.title('$T_{sys}$ using integrated power spectra vs. temperature')
    if dosave:
        plt.savefig('output/plots/tsys_integrated.pdf', format = 'pdf')

def tsys_freq():
    plt.figure(5)
    plt.clf()
    plt.semilogy(freq, tsys_of_f)
    plt.grid(which = 'both')
    plt.xlim(0, 2200)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('$T_{sys}$ (K)')
    plt.title('$T_{sys}$ as a function of frequency')
    if dosave:
        plt.savefig('output/plots/tsys_freq.pdf', format = 'pdf')

def zero_point_power():
    plt.figure(6)
    plt.clf()
    plt.semilogy(freq, rayleigh_jeans)
    plt.grid(which = 'both')
    plt.xlim(0, 2200)
    plt.ylim(10e-23, 10e-19)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Intensity (W /m$^2$ /Hz /Sr)')
    plt.title('Zero-point power spectrum')
    if dosave:
        plt.savefig('output/plots/zero_point_power.pdf', format = 'pdf')
    
if __name__ == '__main__':
    files = {#'cal. 1': 'output/2016-05-10T19:01:58.179458.h5',
       ##'argon': 'output/2016-05-10T19:07:48.457996.h5',
        #'ceiling': 'output/2016-05-10T19:30:38.843197.h5',
       ##'nitrogen': 'output/2016-05-10T19:34:47.613172.h5',
       ##'room temp absorber': 'output/2016-05-10T19:40:04.600969.h5',
        #'nitrogen': 'output/2016-05-10T19:57:36.841898.h5',
        #'cal. 3': 'output/2016-05-10T19:57:36.841898.h5',
        #'room_temp2': 'output/2016-05-10T00:47:17.636651.h5',
        #'room_temp1': 'output/2016-05-09T23:49:40.129530.h5',
        #'possible feedback': 'output/2016-05-12T16:13:05.975114.h5',
        'room temp absorber': 'output/2016-05-12T18:55:20.747231.h5',
        'nitrogen': 'output/2016-05-12T22:57:35.787602.h5',
        }
    data = {key: read_to_arrays(val) for key, val in files.items()} 
    acc_len = 5 #data.values()[1]['acc_len']
    f_ny = 2200 #MHz
    freq = np.linspace(0, f_ny, 2048)
    k_b = 1.38064852e-23
    c = 2.99792458e8
    temp = {'argon': 87.3,
            'nitrogen': 77.2,
            'room temp absorber': 293}
    
    colors = {'argon': 'blue',
              'nitrogen': 'red',
              'room temp absorber': 'green',}
    
    start = 1
    stop = 720
    N = stop - start
    
    spec = {key: val['spec'][start:stop] / (acc_len * f_ny * 1e6 / 2048.)
            for key, val in data.items()}
    avgs = {key: val.mean(axis=0) for key, val in spec.items()}
    stds = {key: val.std(axis=0) for key, val in spec.items()}
    itgl = {key: val.mean() for key, val in avgs.items()}  
    v_of_t = np.array([[temp[key], val] for key, val in itgl.items()])
    slope, intercept = linregress(v_of_t)[:2]
    tsys_of_f = []
    for i in range(2048):
        a = []
        for key, val in avgs.items():
            a.append([temp[key], val[i]])
        a = np.array(a)
        m, b = linregress(a)[:2]
        tsys_of_f.append(b / m)
    tsys_of_f = np.array(tsys_of_f)
    rayleigh_jeans = 2 * (freq*1e6)**2 * k_b * tsys_of_f / c**2

    dosave = False
    power_spectrum_avg()
    power_spectrum_all()
    sigma_over_mu()
    #tsys_integrated()
    #tsys_freq()
    #zero_point_power()

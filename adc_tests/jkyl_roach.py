import numpy as np
import matplotlib.pyplot as plt
import adc5g
import sys
import math
import time
from corr import katcp_wrapper
from fit_cores import fit_snap
from scipy.fftpack import fft
from scipy.signal import blackman

IP = '128.135.52.192'

class Roach:
    def __init__(self, samp_rate, ip = IP):
        self.SNAP_NAME = "scope_raw_0_snap"
        self.SNAP_SIZE = 16384
        self.ZDOK = 0
        self.SAMP_RATE = float(samp_rate)
        self.BOF_FILE = 'adc5g_test_rev2.bof.gz'
        self.TEST_FREQ = None
        self.roach = katcp_wrapper.FpgaClient(ip)
        print('loading .bof file...')
        self.load_bof()
        print('deglitching...')
        self.deglitch()

    def load_bof(self, n = 0):
        try:
            self.roach.progdev(self.BOF_FILE)
            print('success')
        except RuntimeError:
            n += 1
            print('timed out, retrying ({})'.format(n))
            if n < 5:
                self.load_bof(n)
            else:
                print('\nroach not responding.\n')
                sys.exit()

    def deglitch(self):
        try:
            adc5g.set_test_mode(self.roach, self.ZDOK)
            adc5g.sync_adc(self.roach)
            opt0, glitches0 = adc5g.calibrate_mmcm_phase(self.roach, self.ZDOK, 
                                                         [self.SNAP_NAME,])
            adc5g.unset_test_mode(self.roach, self.ZDOK)
            print('success')
        except RuntimeError:
            print('\ndeglitching failed: check clock source\n')
            sys.exit()
    
    def snap(self):
        return np.array(adc5g.get_snapshot(self.roach, self.SNAP_NAME, 
                                           man_trig=True, wait_period=2))

    def clear_ogp(self):
        for core in range(1, 5):
            adc5g.set_spi_gain(self.roach, self.ZDOK, core, 0)
            adc5g.set_spi_offset(self.roach, self.ZDOK, core, 0)
            adc5g.set_spi_phase(self.roach, self.ZDOK, core, 0)

    def get_ogp(self):
        ogp = np.zeros((12), dtype='float')
        indx = 0
        for chan in range(1,5):
            ogp[indx] = adc5g.get_spi_offset(self.roach, self.ZDOK, chan)
            indx += 1
            ogp[indx] = adc5g.get_spi_gain(self.roach, self.ZDOK, chan)
            indx += 1
            ogp[indx] = adc5g.get_spi_phase(self.roach, self.ZDOK, chan)
            indx += 1
        return ogp.reshape(4, 3)
    
    def is_calibrated(self):
        return not np.all(self.get_ogp() == 0)

    def fit_ogp(self, freq):
        self.TEST_FREQ = freq
        snap = self.snap()
        for i in (0, 1):
            ogp_fit, sinad = fit_snap(snap, freq, self.SAMP_RATE, "if0", 
                                      clear_avgs = (not i), prnt = True)
        ogp_fit = np.array(ogp_fit)[3:].reshape(4, 3)
        cur_ogp = self.get_ogp()
        t = cur_ogp + ogp_fit
        offs = t[:, 0]
        gains = t[:, 1]
        phase = t[:, 2]
        phase = (phase - phase.min())*.65
        for i in range(len(offs)):
             adc5g.set_spi_offset(self.roach, self.ZDOK, i+1, offs[i])
             adc5g.set_spi_gain(self.roach, self.ZDOK, i+1, gains[i])
             adc5g.set_spi_phase(self.roach, self.ZDOK, i+1, phase[i])

    def plot_snap(self, snap = None, save = False):
        if snap == None:
            snap = self.snap()
        title = ['{} Gs/s'.format(self.SAMP_RATE/1000), 'ogp uncalibrated']
        if self.is_calibrated():
            title[1] = 'ogp calibrated'
        title = ', '.join(title)
        plt.ion()
        plt.clf()
        fig = plt.figure(1)
        plt.title(title)
        for i in range(4):
            x = np.linspace(i, len(snap)+i, len(snap)/4.)
            plt.plot(x, snap[i::4], 'o--', label = 'core {}'.format(i+1))
        plt.xlim(0,400)
        plt.grid()
        plt.legend(loc = 'best')
        plt.xlabel('samples')
        plt.ylabel('amplitude')
        if save:
            fig.set_size_inches(15, 9)
            plt.savefig('output/' + title, format = 'pdf')
            
    def plot_cores(self, snap = None, save = False):
        if snap == None:
            snap = self.snap()
        title = ['{} Gs/s'.format(self.SAMP_RATE/1000), 'ogp uncalibrated']
        if self.is_calibrated():
            title[1] = 'ogp calibrated'
        title = ', '.join(title)
        plt.ion()
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2)
        fig.suptitle(title)
        c = ('b', 'g', 'r', 'c')
        for i, ax in enumerate((ax1, ax2, ax3, ax4)):
            ax.plot(snap[i::4], c[i]+'o--', label = 'core {}'.format(i+1))
            ax.set_xlim(0,300)
            ax.grid()
            ax.legend(loc = 'best')
            ax.set_xlabel('Samples')
            ax.set_ylabel('Amplitude (ADU)')
            ax.set_ylim(-(max(abs(snap.min()), snap.max()) + 1),
                        (max(abs(snap.min()), snap.max()) + 1))
                
        if save:
            fig.set_size_inches(15, 9)
            fig.savefig('output/' + title, format = 'pdf')

    def get_fft(self, core = 'all', integrate = 1, window = False):
        '''
        '''
        start = 0
        step = 1
        if core != 'all':
            start = core - 1
            step = 4
        max_freq = self.SAMP_RATE / (2. * step)
        n_bins = (self.SNAP_SIZE / (2. * step)) + 1
        include_nyquist = np.zeros(n_bins)
        compare = None
        f_bins = np.linspace(0, max_freq, n_bins)
        for i in range(integrate):
            snap = self.snap()[start::step]
            snap = snap - snap.mean()
            if window == 'compare':
                compare = np.copy(include_nyquist)
                windowed, unwindowed = (fft(snap * blackman(snap.size)),
                                        fft(snap))
                power_units = np.abs(np.conj(windowed) * windowed)
                include_nyquist += power_units[:n_bins]
                compare += np.abs(np.conj(unwindowed) * unwindowed)[:n_bins]
            else:
                if window:
                    windowed_fft = fft(snap * blackman(snap.size))
                else:
                    windowed_fft = fft(snap)
                power_units = np.abs(np.conj(windowed_fft) * windowed_fft)
                include_nyquist += power_units[:n_bins]
        rv = include_nyquist / float(integrate)
        if compare != None:
            compare = compare / float(integrate)
        return f_bins, rv, compare
        
    
    def plot_fft(self, log_f = True, integrate = 1,
                 window = False, core = 'all', save = False):
        '''
        '''
        core_downsamp = 1.
        if not core == 'all':
            core_downsamp = 4.
        title = ['{} Gs/s (core: {})'.format(self.SAMP_RATE / (core_downsamp * 1000.), core),
                 '{} integrations ({} $\mu s$ )'.format(integrate,\
                                            (integrate * 16384  / self.SAMP_RATE)),
                 'OGP uncalibrated']
        if self.is_calibrated():
            title[-1] = 'OGP calibrated'
        
        title = '\n'.join(title)
        f_bins, s = self.get_fft(core = core, integrate = integrate,
                                 window = window)
        if log_f:
            s, f_bins = s[1:], f_bins[1:] # discard 0 Hz term (-inf on log scale).    
        plt.ion()
        fig = plt.figure(1)
        c = {'all': 'k', 1: 'b', 2: 'g', 3: 'r', 4: 'c'}
        plt.plot(f_bins, s, color = c[core])
        plt.yscale('log')
        if log_f:
            plt.xscale('log')
        plt.xlim(f_bins[0], f_bins[-1])
        plt.ylim(1, 1e12)
        plt.grid(True, which = 'both')
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Power')
        plt.title(title)
        if save:
            fig.set_size_inches(15, 9)
            plt.savefig('output/fft.pdf', format = 'pdf')

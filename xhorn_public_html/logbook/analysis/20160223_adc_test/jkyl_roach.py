import numpy as np
import matplotlib.pyplot as plt
import adc5g
from corr import katcp_wrapper
from fit_cores import fit_snap

IP = '128.135.52.192'

class Roach:
    def __init__(self, ip):
        self.SNAP_NAME = "scope_raw_0_snap"
        self.ZDOK = 0
        self.SAMP_RATE = 5000.
        self.BOF_FILE = 'adc5g_test_rev2.bof.gz'
        self.roach = katcp_wrapper.FpgaClient(ip)
        self.load_bof()
        self.deglitch()

    def load_bof(self, n = 0):
        try:
            self.roach.progdev(self.BOF_FILE)
            print('succesfully loaded .bof')
        except RuntimeError:
            n += 1
            print('timed out, retrying ({})'.format(n))
            if n <= 10:
                self.load_bof(n)

    def deglitch(self):
        try:
            adc5g.set_test_mode(self.roach, self.ZDOK)
            adc5g.sync_adc(self.roach)
            opt0, glitches0 = adc5g.calibrate_mmcm_phase(self.roach, self.ZDOK, 
                                                         [self.SNAP_NAME,])
            adc5g.unset_test_mode(self.roach, self.ZDOK)
            print('succesfully deglitched')
        except RuntimeError:
            print('deglitching failed: check clock source')
    
    def snap(self):
        return np.array(adc5g.get_snapshot(self.roach, self.SNAP_NAME, 
                                           man_trig=True, wait_period=2))

    def clear_ogp(self):
        for core in range(1,5):
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

    def fit_ogp(self, freq):
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

        adc5g.set_spi_control(self.roach, self.ZDOK)
        for i in range(len(offs)):
             adc5g.set_spi_offset(self.roach, self.ZDOK, i+1, offs[i])
             adc5g.set_spi_gain(self.roach, self.ZDOK, i+1, gains[i])
             adc5g.set_spi_phase(self.roach, self.ZDOK, i+1, phase[i])

    def plot_snap(self):
        snap = self.snap()
        plt.ion()
        plt.clf()
        fig = plt.figure(1)
        plt.title('{} Gs/s after calibrating OGP'.format(int(self.SAMP_RATE/1000.)))
        for i in range(4):
            x = np.linspace(i, len(snap)+i, len(snap)/4.)
            plt.plot(x, snap[i::4], 'o--', label = 'core {}'.format(i+1))
        plt.xlim(0,400)
        plt.grid()
        plt.legend(loc = 'best')
        plt.xlabel('samples')
        plt.ylabel('amplitude')
        fig.set_size_inches(15, 9)
        plt.savefig('output/{}G_snapshot.pdf'\
                    .format(int(self.SAMP_RATE/1000.)), format = 'pdf')
            
    def plot_cores(self):
        snap = self.snap()
        plt.ion()
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2)
        fig.suptitle('{} Gs/s after calibrating OGP'.format(int(self.SAMP_RATE/1000.)))
        c = ('b', 'g', 'r', 'c')
        for i, ax in enumerate((ax1, ax2, ax3, ax4)):
            ax.plot(snap[i::4], c[i]+'o--', label = 'core {}'.format(i+1))
            ax.set_xlim(0,100)
            ax.grid()
            ax.legend(loc = 'best')
            ax.set_xlabel('samples')
            ax.set_ylabel('amplitude')
        fig.set_size_inches(15, 9)
        fig.savefig('output/{}G_seperate_cores.pdf'\
                    .format(int(self.SAMP_RATE/1000.)), format = 'pdf')

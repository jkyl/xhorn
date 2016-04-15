import numpy as np
import adc5g as adc
import fit_cores as fit
import matplotlib.pyplot as plt
import corr
import time
import sys
import struct

class Spec:
    
    def __init__(self, acc_len = 1, samp_rate = None, ip = '128.135.52.192'):
        '''
        Initializes a 2048 channel spectrometer by connecting to the given IP, loading 
        simple_spec.bof, deglitching, setting the sample rate (or estimating if none 
        given), setting the accumulation length, setting FFT shift, and arming PPS. 
        '''
        self._n_chans = 2048
        print('Connecting to "{}"'.format(ip))
        self.connect(ip)
        print('Loading "simple_spec.bof"')
        self.load_bof()
        print('Deglitching')
        self.deglitch()
        if samp_rate != None:
            print('Setting sample rate to {} MHz'.format(samp_rate))
        self.set_clock(samp_rate)
        print('Setting accumulation length to {} s'.format(acc_len))
        self.set_acc_len(acc_len)
        print('Setting fft shift')
        self.set_fft_shift()
        print('Arming PPS')
        self.arm_pps() 
        
    def connect(self, ip = '128.135.52.192'):
        '''
        Setter for roach object.
        '''
        roach = corr.katcp_wrapper.FpgaClient(ip)
        time.sleep(1)
        if roach.is_connected():
            self._roach = roach
            self._ip = ip
        else:
            print('Roach not connected, retrying...')
            self.connect(ip)
  
    def load_bof(self, boffile = 'simple_spec.bof'):
        '''
        Setter for boffile.
        '''
        if boffile == 'test':
            boffile = 'adc5g_test_rev2.bof.gz'
        self.roach.progdev(boffile)
        self._boffile = boffile
        time.sleep(0.5)
        
    def deglitch(self):
        '''
        For use with adc5g test boffile. Calibrates phase of clock eye to see peaks 
        and troughs, not zero crossings. 
        '''
        adc.set_test_mode(self.roach, 0)
        adc.sync_adc(self.roach)
        opt0, glitches0 = adc.calibrate_mmcm_phase(self.roach, 0,
                                                   ['snapshot_adc0',])
        adc.unset_test_mode(self.roach, 0)
        
    def is_calibrated(self):
        '''
        Returns False if every element of the OGP matrix is 0, True otherwise. 
        '''
        return not np.all(self.get_ogp() == 0)

    def clear_ogp(self):
        '''
        Clears the OGP registers on the ADC.
        '''
        for core in range(1, 5):
            adc.set_spi_gain(self.roach, 0, core, 0)
            adc.set_spi_offset(self.roach, 0, core, 0)
            adc.set_spi_phase(self.roach, 0, core, 0)
            
    def get_ogp(self):
        '''
        Returns the OGP matrix (4 rows of 3 values). 
        '''
        ogp = np.zeros((12), dtype='float')
        indx = 0
        for chan in range(1,5):
            ogp[indx] = adc.get_spi_offset(self.roach, 0, chan)
            indx += 1
            ogp[indx] = adc.get_spi_gain(self.roach, 0, chan)
            indx += 1
            ogp[indx] = adc.get_spi_phase(self.roach, 0, chan)
            indx += 1
        return ogp.reshape(4, 3)

    def fit_ogp(self, freq):
        '''
        Takes a test tone (works best with low frequencies ~10 MHz) and adjusts OGP
        parameters for each core s.t. the residuals are minimized with a least squares
        fit. 
        '''
        snap = self.snap_time()
        for i in (0, 1):
            ogp_fit, sinad = fit.fit_snap(snap, freq, self.samp_rate, 'calibration/if0', 
                                          clear_avgs = (not i), prnt = True)
        ogp_fit = np.array(ogp_fit)[3:].reshape(4, 3)
        cur_ogp = self.get_ogp()
        t = cur_ogp + ogp_fit
        offs = t[:, 0]
        gains = t[:, 1]
        phase = t[:, 2]
        phase = (phase - phase.min())*.65
        for i in range(len(offs)):
             adc.set_spi_offset(self.roach, 0, i+1, offs[i])
             adc.set_spi_gain(self.roach, 0, i+1, gains[i])
             adc.set_spi_phase(self.roach, 0, i+1, phase[i])
             
    def set_clock(self, samp_rate = None):
        '''
        Setter for sample rate / estimates if none given.
        '''
        if not samp_rate == None:
            self._samp_rate = samp_rate
        else:
            print('No sample rate given, estimating...')
            board_clock = self.roach.est_brd_clk()
            time.sleep(0.5)
            self._samp_rate = int(board_clock * 16)
            print('Estimated sample rate: {} MHz.'.format(self._samp_rate))
            
    def set_acc_len(self, acc_len):
        '''
        Setter for acc_len register on roach board.
        '''
        self._acc_len = acc_len
        self.roach.write_int('acc_len',
            int(round(acc_len * self._samp_rate * 1e6 / (16. * self._n_chans))))
        
    def set_fft_shift(self, bitstring = '111111111111'):
        '''
        Setter for fft bitshift.
        '''
        self._fft_shift_int = int(bitstring, 2)
        self.roach.write_int('fft_shift0', self._fft_shift_int)
   
    def arm_pps(self):
        '''
        Setter for pps register on roach board.
        '''
        ctrl = self.roach.read_uint('control')
        ctrl = ctrl | (1<<2)
        self.roach.write_int('control', ctrl)
        ctrl = ctrl & ((2**32 - 1) - (1<<2))
        self.roach.write_int('control', ctrl)

    
    def _snap(self, name, fmt = 'L', man_trig = True):
        '''
        General snap function (can snap time or frequency domain). 
        '''
        wait_period = 2 * self._acc_len
        n_bytes = struct.calcsize('=%s'%fmt)
        d = self.roach.snapshot_get(name, man_trig = man_trig, wait_period = wait_period)
        return np.array(struct.unpack('>%d%s'%(d['length'] / n_bytes, fmt), d['data']))
                
    def snap_spec(self):
        '''
        Snaps the spectrum over the last accumulation. 
        '''
        return self._snap('corr00', fmt = 'q', man_trig = False)

    def snap_time(self):
        '''
        Snaps the last 2^14 samples. 
        '''
        if self.boffile == 'simple_spec.bof':
            return self._snap('snapshot_adc0', fmt = 'b', man_trig = True)
        else:
            return self._snap('scope_raw_0_snap', fmt = 'b', man_trig = True)
        
    def freq_axis(self):
        '''
        Returns frequency bins based on sample rate and number of channels. 
        '''
        return np.arange(0, self._samp_rate / 2., self._samp_rate / 2. / self._n_chans)

    def plot_spec(self):
        '''
        Plots power spectrum over last accumulation. 
        '''
        f, db = self.freq_axis(), 10 * np.log10(self.snap_spec())
        p = plt.plot(f, db, linewidth = 0.4)
        plt.xlim((0, f[-1]))
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Power (dB)')
        plt.grid(True, which = 'both')
        return p
        
    def plot_time(self, cores = False):
        '''
        Plots last 2^14 samples. 
        '''
        t = self.snap_time()
        if cores:
            p = [plt.plot(range(i, t.size + i, 4), t[i::4], 'o--', ms = 4,
                          label = 'Core ' + str(i+1)) for i in range(4)]
            plt.xlim((0, 512))
            plt.legend(loc = 'best')
        else:
            p = plt.plot(t, label = 'All cores')
            plt.xlim((0, 512))
            plt.legend(loc = 'best')
        plt.xlabel('Samples')
        plt.ylabel('Amplitude (ADU)')
        plt.grid(True, which = 'both')
        return p

    @property
    def roach(self):
        return self._roach
    
    @property
    def n_chans(self):
        return self._n_chans

    @property
    def boffile(self):
        return self._boffile

    @property
    def fft_shift(self):
        return self._fft_shift

    @property
    def ip(self):
        return self._ip
    
    @property
    def samp_rate(self):
        return self._samp_rate

    @property
    def acc_len(self):
        return self._acc_len

    

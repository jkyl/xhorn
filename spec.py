import numpy as np
import adc5g as adc
import matplotlib.pyplot as plt
import corr
import time
import sys
import struct

class Spec:
    
    def __init__(self, acc_len = 1, samp_rate = None, deglitch = True,
                 ip = '128.135.52.192'):
        '''
        Initializes a 2048 channel spectrometer by connecting to the given IP, 
        deglitching with adc5g_test_rev2.bof, loading simple_spec.bof, setting 
        the sample rate (or estimating if none given), setting the accumulation 
        length, setting FFT shift, and arming PPS. 
        '''
        self._n_chans = 2048
        print('Connecting to "{}"'.format(ip))
        self.connect(ip)
        if deglitch:
            print('Loading "adc5g_test_rev2.bof.gz"')
            self.load_bof('adc5g_test_rev2.bof.gz')
            print('Deglitching')
            self.deglitch()
        else:
            print('Skipping deglitching')
        print('Loading "simple_spec.bof"')
        self.load_bof('simple_spec.bof')
        if samp_rate != None:
            print('Setting sample rate to {} MHz'.format(samp_rate))
        self.set_clock(samp_rate)
        print('Setting accumulation length to {} s'.format(acc_len))
        self.set_acc_len(acc_len)
        print('Setting fft shift')
        self.set_fft_shift('111111111111')
        print('Arming PPS')
        self.arm_pps()    
        
    def connect(self, ip):
        '''
        Setter for roach object.
        '''
        roach = corr.katcp_wrapper.FpgaClient(ip)
        time.sleep(1)
        if roach.is_connected():
            self._roach = roach
        else:
            print('Roach not connected.')
            sys.exit()
  
    def load_bof(self, boffile):
        '''
        Setter for boffile.
        '''
        self.roach.progdev(boffile)
        self._boffile = boffile
        time.sleep(0.5)
        
    def deglitch(self):
        '''
        For use with adc5g test boffile. 
        '''
        zdok = 0
        snap_name = 'scope_raw_0_snap'
        adc.set_test_mode(self.roach, zdok)
        adc.sync_adc(self.roach)
        opt0, glitches0 = adc.calibrate_mmcm_phase(self.roach, zdok, [snap_name,])
        adc.unset_test_mode(self.roach, zdok)
            
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
        
    def set_fft_shift(self, bitstring):
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
        Snaps the frequency domain over the last accumulation. 
        '''
        return self._snap('corr00', fmt = 'q', man_trig = False)

    def snap_time(self):
        '''
        Snaps the last 4096 samples. 
        '''
        return self._snap('snapshot_adc0', fmt = 'b', man_trig = True)
        
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
        
    def plot_time(self):
        '''
        Plots last 4096 samples. 
        '''
        t = self.snap_time()
        p = plt.plot(t)
        plt.xlim((0, t.size))
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Power (dB)')
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

    

import numpy as np
import adc5g as adc
import matplotlib.pyplot as plt
import corr
import time
import sys
import struct



class Spec:
    
    def __init__(self, acc_len = 1, samp_rate = None, ip = '128.135.52.192'):
        '''
        '''
        self._n_chans = 2048
        self._boffile = 'simple_spec.bof'
        print('\nConnecting to "{}"'.format(ip))
        self.connect(ip)
        print('Loading .bof file "{}"'.format(self._boffile))
        self.load_bof()
        print('Setting sample rate to {} MHz'.format(samp_rate))
        self.set_clock(samp_rate)
        print('Setting accumulation length to {} second(s)'.format(acc_len))
        self.set_acc_len(acc_len)
        print('Setting fft shift')
        self.set_fft_shift('111111111111')
        print('Arming PPS')
        self.arm_pps()    
        
    def connect(self, ip):
        '''
        '''
        roach = corr.katcp_wrapper.FpgaClient(ip)
        time.sleep(0.5)
        if roach.is_connected():
            self.roach = roach
        else:
            print('Roach not connected. Exiting...\n')
            sys.exit()
  
    def load_bof(self):
        '''
        '''
        self.roach.progdev(self._boffile)
        time.sleep(0.5)
        
    def set_clock(self, samp_rate = None):
        '''
        '''
        if not samp_rate == None:
            self._samp_rate = samp_rate
        else:
            print('No sample rate given, estimating...')
            board_clock = self.roach.est_brd_clk()
            time.sleep(0.5)
            self._samp_rate = int(round(board_clock * 16))
            print('Estimated sample rate: {} MHz.'.format(self._samp_rate))
            
    def set_acc_len(self, acc_len):
        '''
        '''
        self._acc_len = acc_len
        self.roach.write_int('acc_len',
            int(round(acc_len * self._samp_rate * 1e6 / (16 * self._n_chans))))
        
    def set_fft_shift(self, bitstring):
        '''
        '''
        self._fft_shift_int = int(bitstring, 2)
        self.roach.write_int('fft_shift0', self._fft_shift_int)
   
    def arm_pps(self):
        '''
        '''
        ctrl = self.roach.read_uint('control')
        ctrl = ctrl | (1<<2)
        self.roach.write_int('control', ctrl)
        ctrl = ctrl & ((2**32 - 1) - (1<<2))
        self.roach.write_int('control', ctrl)

    
    def _snap(self, name, fmt = 'L', man_trig = True):
        '''
        '''
        wait_period = 2 * self._acc_len
        n_bytes = struct.calcsize('=%s'%fmt)
        t0 = time.time()
        d = self.roach.snapshot_get(name, man_trig = man_trig, wait_period = wait_period)
        print(time.time() - t0)
        return np.array(struct.unpack('>%d%s'%(d['length'] / n_bytes, fmt), d['data']))

    def snap_spec(self):
        '''
        '''
        return self._snap('corr00', fmt = 'q', man_trig = False)

    def snap_time(self):
        '''
        '''
        return self._snap('snapshot_adc0', 'b', man_trig = True)
        
    def freq_axis(self):
        '''
        '''
        return np.linspace(0, self._samp_rate // 2, self._n_chans + 1)[1:]

    def plot_spec(self):
        '''
        '''
        f, a = self.freq_axis, 10 * np.log10((self.snap_spec())
        p = plt.plot(f, a)
        plt.xlim((0, f[-1])
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Power (dB)')
        return p
        
    def plot_time(self):
        '''
        '''
        t = self.snap_time()
        p = plt.plot(t)
        plt.xlim((0, t.size))
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Power (dB)')
        return p
        
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

    

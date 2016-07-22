import vxi11
import signal

class Gen:
    def __init__(self, ip='128.135.52.206'):
        '''
        Initializes the vxi11 object, and raises a RuntimeError if is_connected() 
        returns False.
        '''
        self.instr = vxi11.Instrument(ip)
        if not self.is_connected():
            raise RuntimeError, 'device not found.'
        
    def get_id(self):
        '''
        Returns the ID information of the signal generator.
        '''
        return self.instr.ask('*IDN?')

    def is_connected(self, timeout=2):
        '''
        Attempts to make an ID query. Returns bool of success within timeout (s).
        '''
        def handler(_,__): raise RuntimeError
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)
        try:
            self.get_id()
            signal.alarm(0)
            return True
        except RuntimeError:
            return False
        
    def set_freq(self, f):
        '''
        Sets the generator frequency in GHz. 
        '''
        self.instr.write('freq {} GHz'.format(f))

    def get_freq(self):
        '''
        Returns the generator frequency in GHz.
        '''
        return float(self.instr.ask('FREQ?')) / 1e9
        
    def set_pow(self, p):
        '''
        Sets the generator power in dBm.
        '''
        self.instr.write('POW:AMPL {}dbm'.format(p))

    def get_pow(self):
        '''
        Returns the generator power in dBm.
        '''
        return float(self.instr.ask('POW?'))

    def set_rf(self, on_or_off):
        '''
        Sets the RF output to on or off based on bool or 1/0 arg.
        '''
        self.instr.write(':OUTP {}'.format(int(on_or_off)))

    def get_rf(self):
        '''
        Returns a bool of the RF on/off status.
        '''
        return bool(int(self.instr.ask('OUTP?')))

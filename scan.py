from spec import Spec
from motor import Motor
from optparse import OptionParser
import numpy as np
import sys
import csv


def go(m, s, v = True, home = 0, step = 1, fname = 'data.csv'):
    '''
    '''
    cols = np.array(['angle_deg', 'acc_len_secs', 'samp_rate_mhz'] + list(np.arange(2048)))
    f = open(fname, 'wb')
    wr = csv.writer(f)
    wr.writerow(cols)
    
    
    if v: print('Homing')
    m.move(abst = home)

    pos = 0
    while True:
        while pos < 60:
            if v: print('Integrating')
            for i in range(2):
                spec, acc_len = s.snap_spec()
            wr.writerow([pos, acc_len, s.samp_rate] + list(spec))
            if v: print('Moving {} degrees'.format(step))
            m.move(incr = step)
            pos += step
            
        if v: print('Turning around')
        
        while pos > -60:
            if v: print('Integrating')
            for i in range(2):
                spec, acc_len = s.snap_spec()
            wr.writerow([pos, acc_len, s.samp_rate] + list(spec))
            if v: print('Moving {} degrees'.format(-step))
            m.move(incr = -step)
            pos += -step
            
        
    
if __name__ == '__main__':
    p = OptionParser()
    p.set_usage('%prog [options]')
    p.set_description(__doc__)
    p.add_option('-q', '--quiet',
        dest = 'q', action = 'store_true', default = False, 
        help = 'Quiet mode, False by default.')
    p.add_option('-i', '--ip',
        dest = 'ip', type = 'str', default = '128.135.52.192', 
        help = 'Set IP address for ROACH board. Defaults to 128.135.52.192.')
    p.add_option('-s', '--samp_rate',
        dest = 'samp_rate', type = 'int', default = None, 
        help = 'Set ADC sample rate in MHz. Defaults to None (estimate rate).')
    p.add_option('-a', '--acc_len',
        dest = 'acc_len', type = 'float', default = 1, 
        help = 'Set accumulation length in seconds. Defaults to 1.')
    p.add_option('-p', '--port',
        dest = 'port', type = 'str', default = '/dev/tty.usbserial-AD01XAOK', 
        help = 'Set dev port for VXM controller. Defaults to /dev/tty.usbserial-AD01XAOK.')
    p.add_option('-d', '--degrees',
        dest = 'degrees', type = 'float', default = 1, 
        help = 'Set angular step in degrees. Defaults to 1.')
    p.add_option('-z', '--zero',
        dest = 'zero', type = 'float', default = 0, 
        help = 'Set home angle relative to magnetic home in degrees. Defaults to 0.')
    p.add_option('-g', '--go',
        dest = 'go', action = 'store_true', default = False, 
        help = 'Execute data run. False by default.')
    p.add_option('-f', '--fname',
        dest = 'fname', type = 'str', default = 'data.csv', 
        help = 'Set output filename. Defaults to data.csv.')
    
    opts, args = p.parse_args(sys.argv[1:])
    m = Motor(port = opts.port)
    s = Spec(ip = opts.ip, samp_rate = opts.samp_rate,
             acc_len = opts.acc_len, v = not opts.q)
    if opts.go:
        go(m, s, v = not opts.q, step = opts.degrees,
           home = opts.zero, fname = opts.fname)

    
    


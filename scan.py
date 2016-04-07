from spec import Spec
from motor import Motor
import time_sync as ts
import numpy as np
import sys
import csv


def snap_and_move(m, s, wr, step = 1, pos = 0, fname = 'output/test.csv', n_accs = 10, dt = 0):
    '''
    '''
    if v: print('Integrating')
    for i in range(n_accs):
        spec = s.snap_spec()
        time = ts.true_time(dt)
        wr.writerow([pos, time, s.samp_rate] + spec.tolist())
    if v: print('Moving {} degrees'.format(step))
    if m.move(incr = step):
        return m.position()
    

        
def go(step = 1, 
       home = 0,
       bound = 60,
       fname = 'output/test.csv',
       ip = '128.135.52.192',
       samp_rate = 4400,
       acc_len = 1,
       n_accs = 10):
    '''
    '''
    m = Motor(port = port)
    s = Spec(ip = ip, samp_rate = samp_rate, acc_len = acc_len)
    dt = ts.offset()
    f = open(fname, 'wb')
    wr = csv.writer(f)
    cols = ['angle_deg', 'utc_time', 'samp_rate_mhz'] + np.arange(2048).tolist()
    wr.writerow(cols)
    if v: print('Homing')
    m.move(abst = home)
    pos = 0
    try:
        while True:
            while pos < bound:
                pos = snap_and_move(m, s, wr, step = step, pos = pos,
                                    fname = fname, n_accs = n_accs, dt = dt)
            while pos > -bound:
                pos = snap_and_move(m, s, wr, step = -step, pos = pos,
                                    fname = fname, n_accs = n_accs, dt = dt)

        
    except (KeyboardInterrupt, SystemExit):
        print('\nExiting.')
        sys.exit()
    
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2 and args[1] == 'go':
        go(step = 1, 
           home = 0,
           bound = 60,
           fname = 'output/test.csv',
           ip = '128.135.52.192',
           samp_rate = 4400,
           acc_len = 1,
           n_accs = 10)
    else:
        print('\nUsage: python scan.py go\n')
    
    


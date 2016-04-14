from spec import Spec
from motor import Motor
import time_sync as ts
import in_out as io
import numpy as np
import sys, csv, time, h5py

    
def snap_and_move(m, s, f, pos, acc_len = 1, step = 1, n_accs = 10, dt = 0):
    '''
    Function that gets called recursively in go(). 

    Inputs:
        Required - Motor and Spec objects, hdf5 file object, position of motor.
        Optional - accumulation length in secs, step size in degrees, number of 
                   accumulations, computer's offset from true utc time in secs.

    Outputs:
        Takes a snapshot, calculates true time based on offset, calls io.write_to_hdf5 on 
        the hdf5 file object, then moves the motor and returns its position if the move was 
        succesful. 
    '''
    print('Writing {} {}s integrations:'.format(n_accs, acc_len))
    for i in range(n_accs):
        print(i + 1)
        spec = s.snap_spec()
        true_time = ts.true_time(dt)
        io.write_to_hdf5(f, spec, {'angle_degs': pos,
                                   'utc_time': true_time,
                                   'samp_rate_mhz': s.samp_rate})
    print('Moving {} deg'.format(step))
    if m.incr(step):
        print('Sleeping {}s'.format(acc_len))
        time.sleep(acc_len)
        return m.position()
    else:
        sys.exit()
        
def go(step = 1, home = 0, bound = 60, samp_rate = 4800, acc_len = 1, n_accs = 10,
       port = '/dev/tty.usbserial-AD01XAOK', fname = 'output/test.hdf5', ip = '128.135.52.192'):
    '''
    Main function that creates motor, spec, and hdf5 objects, calculates the computer's offset
    from true time, and calls snap_and_move() in order to sweep the horn through a range of
    elevations and write accumulations and metadata to disk. 

    Inputs:
        Step size in degrees, home angle in degrees, max angle in degrees, sample rate in MHz, 
        accumulation length in seconds, number of accumulations, /dev address of motor controller, 
        output filename, and ip address of roach board. 

    Outputs: 
        None, writes to file. Fails safe by closing the file. 
    '''
    try:
        f = h5py.File(fname, 'w')
        m = Motor(port = port)
        s = Spec(ip = ip, samp_rate = samp_rate, acc_len = acc_len)
        dt = ts.offset()
        print('Determined UTC offset to be {} seconds'.format(round(dt, 6)))
        print('Homing to absolute position of {} deg'.format(home))
        if m.abst(home):
            pos = 0
            while True:
                while pos < bound:
                    pos = snap_and_move(m, s, f, pos, step = step,
                                        acc_len = acc_len, n_accs = n_accs, dt = dt)
                while pos > 0:
                    pos = snap_and_move(m, s, f, pos, step = -step,
                                        acc_len = acc_len, n_accs = n_accs, dt = dt)
    except (KeyboardInterrupt, SystemExit):
        print('\nKeyboardInterrupt / SystemExit\n')
    except Exception as e1:
        print('\nExiting with unexpected exception:\n')
        raise e1
    f.close()
        
    
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 3 and args[2] == 'go':
        
    # edit defaults here
        go(
            step = 1, 
            home = 0,
            bound = 60,
            fname = args[1],
            ip = '128.135.52.192',
            samp_rate = 4800,
            acc_len = 1,
            n_accs = 20
        )
    else:
        print('\nUsage: "python scan.py <output/fname.hdf5> go"')
    
    


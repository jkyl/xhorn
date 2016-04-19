#!/usr/bin/python2.7
from spec import Spec
from motor import Motor
import time_sync as ts
import in_out as io
import numpy as np
import sys, csv, time, h5py

def snap_and_move(m, s, fname, zenith = 0, acc_len = 1, step = 1, n_accs = 10, dt = 0):
    '''
    Function that gets called recursively in go(). Takes a snapshot, calculates true time 
    based on offset, queries the motor position, calls io.write_to_hdf5 on the hdf5 file 
    object, then moves the motor.

    Inputs:
        Required - Motor, Spec, and  hdf5 file objects.
        Optional - zenith angle relative to 0 (degs), accumulation length in secs, step size 
                   in degrees, number of accumulations, computer's offset from true utc time 
                   in secs.
    Outputs:
        None, writes to disk. 
    '''
    print('Integrating...')
    for i in range(n_accs):
        print(i + 1)
        spec = s.snap_spec()
        utc = ts.true_time(dt)
        pos = m.position() - zenith
        mjd = ts.iso_to_mjd(utc)
        io.write_to_hdf5(fname, spec, {'angle_degs': pos,
                                       'utc': utc,
                                       'mjd': mjd,
                                       'samp_rate_mhz': s.samp_rate})
    print('Moving {} deg'.format(step))
    m.incr(step)
        
def go(step = 1, min = 0, max = 60, zenith = 0, samp_rate = 4400, acc_len = 1, n_accs = 20,
       port = '/dev/ttyUSB0', ip = '128.135.52.192', home = True):
    '''
    Main function that creates motor, spec, and hdf5 objects, calculates the computer's offset
    from true time, and calls snap_and_move() in order to sweep the horn through a range of
    elevations and write accumulations and metadata to disk. Closes file and creates a new file
    after each return to zenith.

    Inputs:
        Step size in degrees, zenith angle in degrees, min and max angles in degrees, sample 
        rate in MHz, accumulation length in seconds, number of accumulations, /dev address of 
        motor controller, output filename, and ip address of roach board. 

    Outputs: 
        None,  writes to disk. Fails safe by closing the file. 
    '''
    m = Motor(port = port)
    s = Spec(ip = ip, samp_rate = samp_rate, acc_len = acc_len)
    dt = ts.offset()
    fname = 'output/' + ts.true_time(dt) + '.h5'
    if home:
        print('Homing')
        m.home()
    print('Moving to zenith ({} degs relative to zero)'.format(zenith))
    m.abst(zenith)
    while True:
        while m.position() - zenith + step <= max:
            snap_and_move(m, s, fname, zenith = zenith, acc_len = acc_len,
                          step = step, n_accs = n_accs, dt = dt)
        while m.position() - zenith - step >= min:
            snap_and_move(m, s, fname, zenith = zenith, acc_len = acc_len,
                          step = -step, n_accs = n_accs, dt = dt)   
        dt = ts.offset()
        fname = 'output/' + ts.true_time(dt) + '.h5'
    
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2 and args[1] == 'go':        
    ### edit defaults here ###
        go(
            step = 1, 
            min = 0,
            max = 60,
            zenith = 0,
            samp_rate = 4400,
            acc_len = 1,
            n_accs = 20,
            port = '/dev/ttyUSB0',
            ip = '128.135.52.192',
            home = True
        )
    else:
        print('\nUsage: "python scan.py go"')
    
    


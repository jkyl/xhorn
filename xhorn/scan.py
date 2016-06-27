#!/usr/bin/python2.7
from spec import Spec
from motor import Motor
import time_sync as ts
import in_out as io
import numpy as np
import sys, time, h5py, os, tqdm

CALIBRATOR_POSITION = -80

def scan_range(min, max, n):
    '''
    Calculates a secant-spaced array of angles from min to max and back to min in degrees.
    '''
    am_min, am_max = (1 / np.cos(np.pi * a / 180.) for a in (min, max))
    angs = 180 * np.arccos(1 / np.linspace(am_min, am_max, n)) / np.pi
    return [round(a, 2) for a in np.append(angs, angs[-1::-1])]

def move_and_snap(m, s, fname, zenith = 0, destination = 0, acc_len = 1, n_accs = 10, dt = 0):
    '''
    Function that gets called over a range of airmasses in go(). Moves to the destination, 
    takes a snapshot, calculates true time based on offset, queries the motor position, then 
    calls io.write_to_hdf5 on the hdf5 filename.

    Inputs:
        Required - Motor, Spec, and  hdf5 filename.
        Optional - zenith angle wrt. 0 on the motor (degs), destination wrt. zenith (degs), 
                   accumulation length in secs, step size in degrees, number of accumulations, 
                   computer's offset from true utc time in secs.
    Outputs:
        None, writes to disk. 
    '''
    #print('Moving to {} deg ZA'.format(destination))
    m.abst(destination + zenith)
    #print('Integrating')
    for i in tqdm.trange(n_accs, unit='accs'):
        spec = s.snap_spec()
        utc = ts.true_time(dt)
        pos = m.position()
        mjd = ts.iso_to_mjd(utc)
        io.write_to_hdf5(fname, spec, {
            'angle_degs': pos,
            'utc': utc,
            'mjd': mjd,
            'samp_rate_mhz': s.samp_rate,
            'acc_len_secs': s.acc_len,
            'zenith_degs': zenith
        })

def go(min = 20, max = 50, n_steps = 5, zenith = 0, samp_rate = 4400, acc_len = 1, n_accs = 10,
       port = '/dev/ttyUSB0', ip = '128.135.52.192', home=True, docal=True, indef=True):
    '''
    Main function that creates motor, spec, and hdf5 objects, calculates the computer's offset
    from ntp time, and calls snap_and_move() in order to sweep the horn through a range of
    elevations and write accumulations and metadata to disk. Closes file and creates a new file
    after each return to zenith.

    Inputs:
        Step size in degrees, zenith angle in degrees, min and max angles in degrees, sample 
        rate in MHz, accumulation length in seconds, number of accumulations, /dev address of 
        motor controller, output filename, and ip address of roach board. 

    Outputs: 
        None,  writes to disk and std out.
    '''
    m = Motor(port = port)
    s = Spec(ip = ip, samp_rate = samp_rate, acc_len = acc_len)
    angles = scan_range(min, max, n_steps)
    while True:
        dt = 0 #ts.offset()
        fname = '/'.join(os.path.abspath(io.__file__).split('/')[:-2])\
                + '/output/' + ts.true_time(dt) + '.h5'
        if home:
            #print('Homing')
            m.abst(0)
            m.home()
        if docal:
            move_and_snap(m, s, fname, zenith, CALIBRATOR_POSITION + zenith, acc_len, n_accs, dt)
        for destination in tqdm.tqdm(angles, unit = 'steps'):
            move_and_snap(m, s, fname, zenith, destination, acc_len, n_accs, dt)
        if not indef:
            break
            
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2 and args[1] == 'go':
        go()
    else:
        print('\nUsage: "python scan.py go"')
    


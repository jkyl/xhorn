import time, ntplib
import numpy as np
from datetime import datetime

def offset():
    '''
    Queries the nearest ntp server and returns our offset from true UTC time. 
    '''
    return ntplib.NTPClient().request('0.pool.ntp.org').offset

def true_time(offset):
    '''
    Returns an "isoformatted" string of the true (offset-added) UTC time.
    Verify by changing system time - this still returns true utc time. 
    '''
    return datetime.utcfromtimestamp(time.time() + offset).isoformat().encode('utf-8')

def iso_to_dt(iso):
    '''
    Converts isoformat string to datetime object.
    '''
    return datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%f')

def dt_to_epoch(dt):
    '''
    Converts datetime object to seconds since the epoch. 
    '''
    return (dt - datetime(1970, 1, 1)).total_seconds()

def dt_to_mjd(dt):
    '''
    Converts datetime object to modified julian date.
    '''
    return (dt - datetime(1858, 11, 17)).total_seconds() / (60. * 60. * 24.)

def iso_to_epoch(iso):
    '''
    Converts isoformat string to seconds since the epoch.
    '''
    return dt_to_epoch(iso_to_dt(iso))

def iso_to_mjd(iso):
    '''
    Converts isoformat string to modified julian date. 
    '''
    return dt_to_mjd(iso_to_dt(iso))



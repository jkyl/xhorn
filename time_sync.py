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

def utc_to_epoch(iso):
    '''
    Takes an isoformatted string and returns the corresponding time in seconds past
    the epoch (float). 
    '''
    utc_dt = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%f')
    return (utc_dt - datetime(1970, 1, 1)).total_seconds()

    
    

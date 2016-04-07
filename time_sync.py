import time, ntplib, datetime

def offset():
    return ntplib.NTPClient().request('0.pool.ntp.org').offset

def true_time(offset):
    return datetime.datetime.utcfromtimestamp(time.time() - offset).isoformat()
    
    
    

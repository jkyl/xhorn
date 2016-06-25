import in_out as io
import numpy as np

def mask(specs, angles):
    a = angles.ravel()
    u = np.unique(a)
    n = a.size / u.size
    s = np.split(specs, n)
    return s, a
    
def tsys(specs, angles):
    pass
    

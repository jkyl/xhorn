import in_out as io
import numpy as np

def mask(specs, angles):
    a = angles.ravel()
    u = np.unique(a)
    n = a.size / u.size
    s = np.split(specs, n)
    return s, a.reshape(a.size/n, n)[0]
    
def tsys(specs, angles):
    pass
    

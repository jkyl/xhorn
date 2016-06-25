import in_out as io
import numpy as np
CAL_ANG=-80
def mask(specs, angles):
    cal_specs, cal_angs = (i[np.where(angles==CAL_ANG)] for i in (specs, angles))
    
    return cal_specs, cal_angs
    
def tsys(specs, angles):
    pass
    

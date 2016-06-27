from xhorn import in_out
from numpy import *
from matplotlib.pyplot import *
from copy import deepcopy as dc
from IPython.core.debugger import Tracer; debug_here=Tracer()

# Get attenuator calibration data
caldir='calibration/Traces'
db=array([0,1,2,6,9,10,20])
for k,val in enumerate(db):
    fn='{0}/s21_{1}db.csv'.format(caldir,val)
    print fn
    x=loadtxt(fn,skiprows=3,delimiter=',',usecols=(0,1))
    
    if k==0:
        f=x[:,0]/1e6
        atten=zeros((db.size,x.shape[0]))
        atten[0]=x[:,1]
    else:
        atten[k]=x[:,1]

figure(1)
clf()
subplot(2,2,1)
plot(f,atten.T);
legend(db);
grid('on')
title('attenuators')
ylabel('db')
xlim(0,2500)

# Now get spectrometer data
fn=['2016-06-23T22:29:17.537575.h5',
    '2016-06-23T22:31:37.301340.h5',
    '2016-06-23T22:34:01.737960.h5',
    '2016-06-23T22:36:18.341220.h5',
    '2016-06-23T22:38:09.947450.h5',
    '2016-06-23T22:39:58.656672.h5',
    '2016-06-23T22:41:28.426222.h5',
    '2016-06-23T22:42:47.087653.h5']
fndb=array([1,2,6,9,10,20,1,0])


dat=zeros((len(fn),2048,8)) # First two spectra are bad for some reason
for k,val in enumerate(fn):
    dat0=in_out.read_to_arrays('output/{0}'.format(fn[k]))
    dat[k,:,:]=dat0['spec'][2:,:].T
dat=dat.mean(2)
fdat = linspace(0,4400/2,2048)
fdat = fdat+9500

subplot(2,2,3)
plot(fdat,dat.T);
legend(fndb)
grid('on')
title('measured power')
ylabel('V^2')
xlim(9500,12000)


    
# Interpolate attenuator data
atteninterp=zeros((db.size,2048))
for k in range(db.size):
    atteninterp[k]=interp(fdat,f+9500,atten[k])

subplot(2,2,2)

rmeas=zeros((6,2048))
rpred=zeros((6,2048))
denomind=6

for k,val in enumerate([0,1,2,3,4,5]):
    rmeas[k]=dat[val]/dat[denomind]
    kk=where(db==fndb[val])[0][0]
    rpred[k]=10**((atteninterp[kk]-atteninterp[db==fndb[denomind]])/10)
plot(fdat,10*log10(rmeas.T));
#legend(['P_1db/P_1db','P_2db/P_1db','P_6db/P_1db','P_9db/P_1db','P_10db/P_1db','P_20db/P_1db'])
gca().set_color_cycle(None)
plot(fdat,10*log10(rpred.T),'--')
ylabel('atten dB')
xlabel('f GHz')
title('dashed = pred., solid = meas.')



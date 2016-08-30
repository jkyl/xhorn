from numpy import *
from matplotlib.pyplot import *
from copy import deepcopy as dc

###################
# Get attenuator calibration data
caldir='calibration/Traces/'
fn=caldir+'s11_cplx_metal.csv'
x=loadtxt(fn,skiprows=3,delimiter=',',usecols=(0,1,2))
v_metal=x[:,1]+x[:,2]*1j

fn=caldir+'s11_cplx_vhp.csv'
x=loadtxt(fn,skiprows=3,delimiter=',',usecols=(0,1,2))
v_vhp=x[:,1]+x[:,2]*1j

fn=caldir+'s11_cplx_crv.csv'
x=loadtxt(fn,skiprows=3,delimiter=',',usecols=(0,1,2))
v_crv=x[:,1]+x[:,2]*1j

f=x[:,0]
df=(f[2]-f[1])
tmax=1/(2*df)
t=linspace(-tmax,tmax,f.size)

ft_metal=fft.fft(v_metal)
ft_vhp=fft.fft(v_vhp)
ft_crv=fft.fft(v_crv)

clf();
plot(t,abs(ft_metal))
plot(t,abs(ft_vhp))
plot(t,abs(ft_crv))
legend(['metal','vhp','crv'])

from numpy import *
from matplotlib.pyplot import *
from scipy.interpolate import interp1d
from scipy import loadtxt 

a,b=loadtxt('xhorn_nobaffle.tsv',unpack=True,usecols=[0,1])
profile=interp1d(a,b)

nang=1000
x=linspace(-180,180,nang)
xx,yy=meshgrid(x,x)
r=sqrt(xx**2 + yy**2)

errorbar(x,10*log10(profile(r[(nang/2.)])),yerr=.1*log10(profile(r[(nang/2.)])),fmt='k',linewidth=2.0)

inchmin=0
inchmax=11
dinch=1
d=78.

for k in arange(inchmin,inchmax,dinch):
    angle=arctan(k/d)*180./pi
    n=(abs(x-angle).argmin())
    plot(x,(10*log10(profile(r[n])))-(10*log10((profile(r[n])).max())),':',label='%s\"'%(k))

xlabel('Angle (deg)')
ylabel('Power (dB)')
legend(loc='best')
show()

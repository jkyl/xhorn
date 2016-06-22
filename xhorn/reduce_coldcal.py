from xhorn import in_out
from numpy import *
import itertools

dc=in_out.read_time_range((2016,06,17,22,56,45),(2016,06,17,23,8,0))
dat=1.0*dc['spec']
nf=dat.shape[1]
nt=dat.shape[0]




#P1/P2
sind=array([0,50,150,350])
y=zeros((sind.size,nf))

for k,val in enumerate(sind):
    s=sind[k]
    try:
        e=sind[k+1]
    except:
        e=dat.shape[0]

    y[k,:]=1.0*dat[s:e,:].mean(0)

fitind=arange(200)+750
fitind=fitind[fitind!=1024]

xx=list(itertools.combinations(arange(sind.size), 2))

delta=zeros((len(xx),nf))
for k,val in enumerate(xx):
    r=y[val[1]]/y[val[0]]
    rbar=mean(r[fitind])
    delta[k,:]=(r/rbar-1)/log(r)


delta[:,0:500]=0
delta[:,1024]=0



zaa=unique(d.za[d.getscanind()])
sig=np.zeros((zaa.size,d.nscan-1,d.nf-2))
for j,val in enumerate(zaa):
    for k in range(d.nscan-1):
        # za 1
        ind=where((d.za==val) & (d.scan==k))[0]
        y=d.spec[ind].mean(0);
        xs=y[1:-1]-y[0:-2]
        
        # cal
        y=d.c[k]
        xc=y[1:-1]-y[0:-2]
        
        # sig - cal resid
        kk=xs/xc
        fac=median(kk[isfinite(kk)])
        sig[j,k,:]=xs-fac*xc

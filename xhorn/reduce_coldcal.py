from xhorn import in_out
from numpy import *
import itertools

c=in_out.read_time_range((2016,06,17,22,56,45),(2016,06,17,23,8,0))
dat=1.0*c['spec']
nf=dat.shape[1]
nt=dat.shape[0]

u,s,v=linalg.svd(c['spec'])

# Get scanning data
d=reduc_spec.data((2016,06,17,23,27,41),(2016,06,18,0,27,41))
x=d.f-d.f.mean()
a=zeros((x.size,3))
for k in range(a.shape[1]):
    a[:,k]=x**k
    a[:,k]=a[:,k]/a[-1,k]
for k in range(20):
    a=vstack((a.T,v[k,:])).T
fitind=arange(500)+500

y=d.spec[10]/d.g[0]-d.Trx[0]
p=linalg.lstsq(a[fitind,:],y[fitind])[0]
yfit=dot(a,p)



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

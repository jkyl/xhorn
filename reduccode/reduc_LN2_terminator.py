from numpy import *
from matplotlib.pyplot import *
from copy import deepcopy as dc

# Load data


figext='nolid'

if 0:
    # Terminator runs
    #x=load('lab_spec_data/2016-07-28T17:39:15.npz') #1st terminator run
    x=load('lab_spec_data/2016-07-29T17:10:35.npz') #2nd terminator run
    z=x['spec']
    lo=x['LO_freq']
    t=x['time']
    # Cooling down data
    hind=arange(6) # 290 K indices
    cind=-hind-1
    Th=290.0
    Tc=77.0


if 0:
    # metal box LN2 eccosorb run with pyramidal horn
    x1=load('lab_spec_data/2016-07-29T18:12:42.npz') 
    x2=load('lab_spec_data/2016-07-29T18:22:48.npz') 
    z=concatenate((x1['spec'],x2['spec']))
    lo=concatenate((x1['LO_freq'],x2['LO_freq']))
    t=concatenate((x1['time'],x2['time']))
    # State change at index 520
    z=z[0:516]
    lo=lo[0:516]
    t=t[0:516]
    # For warming up data
    cind=arange(15)
    hind=-cind-1
    Th=290.0
    Tc=180.0

if 0:
    # metal box LN2 eccosorb run with corrugated horn
    x1=load('lab_spec_data/2016-07-30T15:21:56.npz') 
    x2=load('lab_spec_data/2016-07-30T15:32:01.npz')
    z=concatenate((x1['spec'],x2['spec']))
    lo=concatenate((x1['LO_freq'],x2['LO_freq']))
    t=concatenate((x1['time'],x2['time']+x1['time'][-1]+2))
    #For warming up data
    cind=arange(15)
    hind=-cind-1
    Th=290.0
    Tc=200.0

if 0:
    # metal box LN2 eccosorb run with corrugated horn run 2
    x=load('lab_spec_data/2016-07-30T17:06:57.npz')
    z=x['spec']
    lo=x['LO_freq']
    t=x['time']
    #For warming up data
    cind=arange(15)
    hind=-cind-1
    Th=290.0
    Tc=200.0

if 1:
    # wood box LN2 eccosorb run with corrugated horn
    #x=load('lab_spec_data/2016-07-30T17:41:22.npz') # Run 1
    #Th=290.0
    #Tc=200.0

    x=load('lab_spec_data/2016-07-30T18:09:07.npz') # Run 2
    Th=290.0
    Tc=180.0

    z=x['spec']
    lo=x['LO_freq']
    t=x['time']
    #For warming up data
    cind=arange(15)
    hind=-cind-1

if 0:
    # wood box LN2 eccosorb run with baffled corrugated horn,
    # just prior to putting on new lid
    x=load('lab_spec_data/2016-08-17T16:04:04.npz') 
    z=x['spec']
    lo=x['LO_freq']
    t=x['time']
    #For warming up data
    cind=arange(30)
    hind=-cind-1
    Th=290.0
    Tc=150.0

if 1:
    # wood box LN2 eccosorb run with baffled corrugated horn,
    # after putting on new lid
    x=load('lab_spec_data/2016-08-17T16:41:02.npz') 
    z=x['spec']
    lo=x['LO_freq']
    t=x['time']
    #For warming up data
    cind=arange(100)
    hind=-cind-1
    Th=290.0
    Tc=140.0


f=linspace(0,2200,z.shape[1])



loval=unique(lo)
nlo=loval.size

zz=[]
tt=[]
for k,val in enumerate(loval):
    zz.append(z[lo==val])
    tt.append(t[lo==val])
zz=array(zz)
tt=array(tt)

############
# Get Tsys

# For cooling down data


Tsys=[]
g=[]
b=[]
for k in range(nlo):
    zh=zz[k,hind,:].mean(0)
    zc=zz[k,cind,:].mean(0)
    
    # Gain, zero point
    g.append((zh-zc)/(Th-Tc))
    b.append(zc-g[k]*Tc)

    Tsys.append(b[k]/g[k])


Tsys=array(Tsys)
g=array(g)
b=array(b)


###############
# Reduce intermediate data given gain and zero point
ntz=zz.shape[1]
bb=swapaxes(tile(b,(ntz,1,1)),0,1)
gg=swapaxes(tile(g,(ntz,1,1)),0,1)
zcal=(zz-bb)/gg

# Fit
zred=dc(zcal)
fitind = where((f>400) & (f<2000))
for k in range(nlo):
    for j in range(ntz):
        x=f[fitind]
        y=zred[k,j,fitind].flatten()
        p=polyfit(x,y,4)
        zred[k,j]=zred[k,j]-poly1d(p)(f)


# Inverse variance weighted mean
#var=zeros((nlo,ntz))
#for k in range(nlo):
#    for j in range(ntz):
#        var[k,j]=std(zred[k,j,fitind])**2
#w=tile(expand_dims(1/var,2),(1,1,2048))
#zmean=sum((zred*w)[:,20:30,:],1)/sum(w[:,20:30,:],1)
#zmean=sum(zred*w,1)/sum(w,1)
zmean=mean(zred,1)


#close('all')

###############
figure(1)
clf()
plot(f,Tsys.T)
ylim(0,150)
legend(['$f_{{LO}}$={:0.0f} MHz'.format(val*1000) for k,val in enumerate(loval)],
       loc='lower right')
xlabel('f (MHz)')
ylabel('Tsys (K)')
grid('on')

###############
figure(2,figsize=(8,10))
clf()
subplot(2,1,1)
plot(f,zmean.T)
title('mean calibrated,  p4 subtracted spectrum')
ylim(-2,2)
ylabel('T (K)')
legend(['$f_{{LO}}$={:0.0f} MHz'.format(val*1000) for k,val in enumerate(loval)])

subplot(2,1,2)
plot(f,zmean[0])
df=f[1]-f[0]
plot(f,roll(zmean[1],int(round((loval[1]-loval[0])*1000/df))))
plot(f,roll(zmean[2],int(round((loval[2]-loval[0])*1000/df))))
ylim(-2,2)
title('frequency shifted')
ylabel('T (K)')
xlabel('f (MHz)')

###############
figure(3)
clf()
r1=(zz[0,ntz-1]-zz[0,0])/(zz[0,50]-zz[0,0])
r2=(zz[1,ntz-1]-zz[1,0])/(zz[1,50]-zz[1,0])
clf();plot(f,r1);xlim(1050,1500);
plot(f,roll(r2,51));xlim(1050,1500);
ylim(0,4)
xlabel('f (MHz)')
ylabel('ratio')
title('raw spectrum [P(last)-P(first)]/[P(intermediate)-P(first)]')
legend(['$f_{{LO}}$={:0.0f}'.format(loval[0]*1000),
        'frequency shifted $f_{{LO}}$={:0.0f}'.format(loval[1]*1000)],
       loc='lower right')
       

###############
figure(4,figsize=(8,10))
clf()

subplot(3,1,1)
plot(f,zz[2,:,:].T)
xlabel('f (MHz)')
ylabel('ADU^2')
text(.99,.02,'raw spectra',
      verticalalignment='bottom',horizontalalignment='right',transform=gca().transAxes)
text(.99,.98,'$f_{{LO}}$={:0.0f} MHz'.format(loval[2]),
      verticalalignment='top',horizontalalignment='right',transform=gca().transAxes)

subplot(3,1,2)
plot(tt[0],zz[0,:,1200])
plot(tt[1],zz[1,:,1200])
plot(tt[2],zz[2,:,1200])
text(.99,.02,'raw spectrum, f = {:0.2f} MHz channel'.format(f[1200]),
      verticalalignment='bottom',horizontalalignment='right',transform=gca().transAxes)
legend(['$f_{{LO}}$={:0.0f} MHz'.format(val*1000) for k,val in enumerate(loval)])
xlabel('t (s)');
ylabel('ADU^2')

subplot(3,1,3)
plot(f,zcal[2,:,:].T)
ylim(70,300)
xlabel('f (MHz)')
ylabel('T (K)')
text(.99,.02,'calibrated spectra'.format(f[1200]),
      verticalalignment='bottom',horizontalalignment='right',transform=gca().transAxes)


dosave=False
if dosave:
    for k in (array(range(4))+1):
        figure(k)
        savefig('fig_{0}_{1}.png'.format(k,figext))
        

from numpy import *
from matplotlib.pyplot import *

def loaddata(fname):
    x=loadtxt(fname,delimiter=',',comments='#',dtype='string').T
    hdr=x[0:9,0].astype('S64')
    dat=x[0:9,1:].astype('float')

    x=dat[0]
    y=dat[[5,6,7,8],:]
    leg=hdr[[5,6,7,8]]

    for k,val in enumerate(leg):
        leg[k]=leg[k][5:]

    return x,y,leg

f,y9p5,leg=loaddata('s21_-20dbm_lo9p5.csv')
f,y9p4,leg=loaddata('s21_-20dbm_lo9p4.csv')

figure(1,figsize=(8,10))
clf()
plot(f/1e9,y9p5.T);
gca().set_color_cycle(None)
plot(f/1e9,y9p4.T,':')
xlabel('f (GHz)')
ylabel('dB');
ylim(-100,10)
leg[1]=leg[1]+' (- 65 dB)'
legend(leg,loc='upper right')
title('Input power = -20 dBm, {solid/dashed} = LO {9.5/9.4} GHz')
grid('on')

figure(2,figsize=(8,10))
clf()
p,y,dum=loaddata('s21_10p5ghz_lo9p5.csv')

col=['b','g','r','c']
for k in range(4):
    ax=subplot(4,1,k+1)
    plot(p,y[k],col[k],label=leg[k])
    grid('on')
    legend()
    if k==0:
        title('At 10.5 GHz, L0 = 9.5 GHz')
xlabel('Power (dBm)')
ylabel('dB')

for k in array(range(2))+1:
    figure(k)
    savefig('fig_{0}.png'.format(k))

from xhorn import reduc_spec

doload=False
if doload:
    d = reduc_spec.data( (2016,8,22,23,23,54) , (2016,8,23,15,36,16) )
    d.fitam(zarange=[40,41])
    exind=d.expandcal()
    x=(d.spec - d.b[exind])/d.g[exind]

za=unique(d.za)
f=d.f+d.lo

    
figure(1)
clf()
h=plot(f,d.Trx.mean(0),'b')
ylim(50,150)
grid('on')
ylabel('Tsys (K)')
xlabel('f (MHz')
title('mean Tsys over {0} x 3 min scans'.format(d.nscan))
grid('on')

figure(2,figsize=(14,10))
clf()
col=['b','g','r','m','c']
h=[]
for j,val in enumerate(za[1:]):
    hh=plot(f,x[(d.za==val)].mean(0),
            color=col[j],label='za={:0.1f} deg'.format(val))
    h.append(hh[0])
legend()
ylabel('Tant (K)')
xlabel('f (MHz)')
grid('on')
ylim(3,8)

figure(3)
clf()
plot(f,x[d.getcalind()].mean(0))
xlabel('f (MHz)')
ylabel('Tant (K)')
title('VHP cone calibrated spectra mean over scans')
grid('on')
ylim(290,291)


figure(4,figsize=(22,14))
clf()
cl=[ [-1.5,1.5], [-.5,.5], [-.5,.5], [-.5,.5], [-1,1]]

sind=d.getscanind()
for k,val in enumerate(za[1:]):
    subplot(1,5,k+1)
    imshow((x[d.za==val].T-nanmean(x[d.za==val,700:1000],1)).T,
           extent=[f[0],f[-1],d.t[-1],0])
    cll=cl[k]
    clim(cll)
    grid('on')
    #c=colorbar();c.set_label('T (K)')
    title('za = {:0.1f}, clim={:0.1f}-{:0.1f} K'.format(val,cll[0],cll[1]))
    if k==0:
        ylabel('hours since 6:30 pm')
    xlim(10200,10400)



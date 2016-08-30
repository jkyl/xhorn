from xhorn import reduc_spec

doload=False

if doload:
    # Load last 30 min of data prior to removing baffle, and first thiry minutes
    # after removing it
    d_on=reduc_spec.data( (2016,8,23,16,06,16),(2016,8,23,16,36,30) )
    d_off=reduc_spec.data( (2016,8,23,16,50,11),(2016,8,23,17,20,11) )
    
    d_on.fitam(zarange=[40,41])
    d_off.fitam(zarange=[40,41])

    cind=d_on.getcalind();

    exind=d_on.expandcal()
    xon=(d_on.spec - d_on.b[exind])/d_on.g[exind]
    xoff=(d_off.spec - d_off.b[exind])/d_off.g[exind]

    za=unique(d_on.za)
    f=d_on.f+d_on.lo

figure(1)
clf()
h1=plot(f,d_on.Trx.T,'b')
h2=plot(f,d_off.Trx.T,'g')
ylim(50,150)
legend([h1[0],h2[0]],['baffle on','baffle off'])
grid('on')
ylabel('Tsys (K)')
xlabel('f (MHz')
title('variation over 10 x 3 min scans')
grid('on')

figure(2,figsize=(14,10))
clf()
col=['b','g','r','m','c']
hon=[]
for scan in range(d_on.nscan):
    gca().set_color_cycle(None)
    for j,val in enumerate(za[1:]):
        honn=plot(f,xon[(d_on.za==val) & (d_on.scan==scan)].mean(0),
                  color=col[j],label='za={:0.1f} deg, baffle on'.format(val))
        hon.append(honn[0])
        hoff=plot(f,xoff[(d_off.za==val) & (d_off.scan==scan)].mean(0),
                  color='k',linestyle=':',label='same za''s, baffle off')
ylim(3,8)
x=hon[0:5]+hoff
leg=[]
legend(x,[val.get_label() for k,val in enumerate(x)])
ylabel('Tant (K)')
xlabel('f (MHz)')
grid('on')

figure(3)
clf()
for k in range(d_on.nscan):
    hon=plot(f,xon[d_on.getcalind(k)].mean(0),'b')
    hoff=plot(f,xoff[d_on.getcalind(k)].mean(0),'g')
xlabel('f (MHz)')
ylabel('Tant (K)')
title('VHP cone calibrated spectra')
legend([hon[0],hoff[0]],['baffle on','baffle off'])
grid('on')
ylim(285,295)


figure(4,figsize=(22,12))
clf()
cl=[ [-1.5,1.5], [-.5,.5], [-.5,.5], [-.5,.5], [-1,1]]

sind=d_on.getscanind()
for k,val in enumerate(za[1:]):
    subplot(5,2,2*k+1)
    imshow((xon[d_on.za==val].T-nanmean(xon[d_on.za==val,700:1000],1)).T,
           extent=[f[0],f[-1],200,0])
    clim(cl[k])
    grid('on')
    c=colorbar();c.set_label('T (K)')
    if k==0:
        title('baffle on')
    h=ylabel('za = {:0.1f}'.format(val),fontsize=14);h.set_rotation(0)
    xlim(10000,10750)

    subplot(5,2,2*k+2)
    imshow((xoff[d_on.za==val].T-nanmean(xoff[d_on.za==val,700:1000],1)).T,
           extent=[f[0],f[-1],200,0])
    clim(cl[k])
    grid('on')
    c=colorbar();c.set_label('T (K)')
    if k==0:
        title('baffle off')
    xlim(10000,10750)



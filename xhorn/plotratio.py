d=reduc_spec.data((2016,6,25,5,13,45),(2016,6,25,5,45,0))
d.reduc()

sind=d.getscanind()
za=unique(d.za[sind])
am=d.za2am(za)

for k in range(d.nscan):
    ind1=where((d.scan==k) & (d.za==za[0]))[0]
    ind2=where((d.scan==k) & (d.za==za[4]))[0]
    #plot( (d.spec[ind1].mean(0) - d.b[k] )/(d.spec[ind2].mean(0)- d.b[k] ));
    sm=d.spec[d.getscanind(k)].mean(0)
    plot( (d.spec[ind1].mean(0) - sm )/(d.spec[ind2].mean(0)- sm ));

amm=d.am[d.getscanind()].mean()
plot([0,2000],tile((am[0]-amm)/(am[4]-amm),(2,1)))



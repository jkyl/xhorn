from xhorn import reduc_spec

doload=True
if doload:
    d=reduc_spec.data( (2016,8,23,22,59,13) , (2016,8,23,23,17,39) )
    d=d.splitbylo(9.5)
    d.fitam([0,90])
    x=(d.spec-d.b[d.expandcal()])/d.g[d.expandcal()]
    za=unique(d.za)

clf()
for k,val in enumerate(za[1:]):
    plot(x[ (d.za==val) & (d.scan==1) ].mean(0));
gca().set_color_cycle(None)
for k,val in enumerate(za[1:]):
    plot(x[ (d.za==val) & (d.scan==2) ].mean(0),linestyle=':');
ylim(0,10)

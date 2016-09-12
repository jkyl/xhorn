from xhorn import reduc_spec
from numpy import *
from matplotlib.pyplot import *
import sys


BAFF = ((2016, 8, 22, 22, 23), 
        (2016, 8, 23, 0, 33))

NOBAFF = ((2016, 8, 23, 16, 50),     
          (2016, 8, 23, 18, 50))

ECCO = ((2016, 8, 29, 20, 54),      
        (2016, 8, 29, 21, 40))

NOECCO = ((2016, 8, 23, 16, 50),    
          (2016, 8, 23, 17, 25))

NOECCO_CONTAM = ((2016, 8, 29, 21, 50),
                 (2016, 8, 29, 22, 40))

NEWNO = ((2016, 9, 9, 17, 42),
         (2016, 9, 9, 18, 26))

NEWNO_2 = ((2016, 9, 9, 17, 0),
           (2016, 9, 9, 17, 44))

NEWEC = ((2016, 9, 9, 18, 49),
         (2016, 9, 9, 19, 30))

NEWLIP = ((2016, 9, 9, 19, 36),
          (2016, 9, 9, 20, 20))

class sky:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

def doload(on, off):
    # Load last 30 min of data prior to removing baffle, and first thiry minutes
    # after removing it
    d = {}
    d_on, d_off = (reduc_spec.data(*time) for time in (on, off))
    exind = d_on.expandcal()
    cind = d_on.getcalind()
    for a in (d_on, d_off):
        a.fitam(zarange=[40,41]) 
    d['xon'], d['xoff'] = ((a.spec - a.b[exind]) / a.g[exind]\
                               for a in (d_on, d_off))
    d['d_on'], d['d_off'], d['exind'], d['cind'], d['za'], d['f'] = \
        (d_on, d_off, exind,  cind, unique(d_on.za), d_on.f+unique(d_on.lo)[0]*1e3)
    return sky(**d)

def tsys(s):
    figure(1)
    clf()
    h1=plot(s.f,s.d_on.Trx.T,'b')
    h2=plot(s.f,s.d_off.Trx.T,'g')
    ylim(50,150)
    legend([h1[0],h2[0]],['baffle on','baffle off'])
    grid('on')
    ylabel('Tsys (K)')
    xlabel('f (MHz')
    title('variation over 10 x 3 min scans')
    grid('on')

def tant(s):
    figure(2,figsize=(14,10))
    clf()
    col=['b','g','r','m','c']
    hon=[]
    for scan in range(s.d_on.nscan):
        gca().set_color_cycle(None)
        for j,val in enumerate(s.za[1:]):
            honn=plot(s.f,s.xon[(s.d_on.za==val) & (s.d_on.scan==scan)].mean(0),
                      color=col[j],label='za={:0.1f} deg, baffle on'.format(val))
            hon.append(honn[0])
            hoff=plot(s.f,s.xoff[(s.d_off.za==val) & (s.d_off.scan==scan)].mean(0),
                      color='k',linestyle=':',label='same za''s, baffle off')
    ylim(3,8)
    x=hon[0:5]+hoff
    leg=[]
    legend(x,[val.get_label() for k,val in enumerate(x)])
    ylabel('Tant (K)')
    xlabel('f (MHz)')
    grid('on')

def tcal(s):
    figure(3)
    clf()
    for k in range(s.d_on.nscan):
        hon=plot(s.f,s.xon[s.d_on.getcalind(k)].mean(0),'b')
        hoff=plot(s.f,s.xoff[s.d_on.getcalind(k)].mean(0),'g')
    xlabel('f (MHz)')
    ylabel('Tant (K)')
    title('VHP cone calibrated spectra')
    legend([hon[0],hoff[0]],['baffle on','baffle off'])
    grid('on')
    ylim(285,295)

def ims(s):
    fig = figure(4,figsize=(22,12))
    clf()
    cl=[ [-1.5,1.5], [-.5,.5], [-.5,.5], [-.5,.5], [-1,1]]
    sind=s.d_on.getscanind()
    for k,val in enumerate(s.za[1:]):
        subplot(5,2,2*k+1)
        imshow((s.xon[s.d_on.za==val].T-nanmean(s.xon[s.d_on.za==val,700:1000],1)).T,
               extent=[s.f[0],s.f[-1],200,0])
        #clim(cl[k])
        clim(-1.5, 1.5)
        grid('on')
        #c=colorbar();c.set_label('T (K)')
        if k==0:
            title('on')
        h=ylabel('za = {:0.1f}'.format(val),fontsize=14)
        #xlim(10000,10750)

        subplot(5,2,2*k+2)
        imshow((s.xoff[s.d_on.za==val].T-nanmean(s.xoff[s.d_on.za==val,700:1000],1)).T,
               extent=[s.f[0],s.f[-1],200,0])
        #clim(cl[k])
        clim(-1.5, 1.5)
        grid('on')
        #c=colorbar();c.set_label('T (K)')
        if k==0:
            title('off')
        #xlim(10000,10750)
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
        c=colorbar(cax=cbar_ax);c.set_label('T (K)')

def means(s, titles=('on', 'off')):
    figure(5);clf()
    fig, axes2d = subplots(num=5, nrows=5, ncols=2,
                           sharex=True, sharey=True,
                           figsize=(22,12))
    sind=s.d_on.getscanind()
    for i, row in enumerate(axes2d):
        for j, cell in enumerate(row):
            on_or_off = (s.xon, s.xoff)[j]
            if i == 0:
                cell.set_title(titles[j])
            if j == 1:
                cell.set_ylabel(s.za[i+1])
                cell.yaxis.set_label_position("right")
            data = nanmean((on_or_off[s.d_on.za==s.za[i+1]].T\
                                -nanmean(on_or_off[s.d_on.za==s.za[i+1],700:1000],1)).T,0)
            cell.plot(s.f, data, color='bgrcm'[i])
            cell.set_xlim(s.f[0], s.f[-1])
            cell.set_xticks(linspace(s.f[0], s.f[-1], 12))
            cell.set_xticklabels((round(a,1) for a in linspace(s.f[0], s.f[-1], 12) / 1e3), rotation='vertical')
            cell.set_ylim(-5, 5)
            cell.grid(True)
    fig.text(0.5, 0.97, 'Calibrated spectra\'s deviation from median ZA\'s, mean-subtracted and averaged over {} scans.'.format(s.d_on.nscan), ha='center', fontsize=15)
    fig.text(0.06, 0.5, 'T (K)', va='center', rotation='vertical')
    fig.text(0.94, 0.5, 'ZA (deg)', va='center', rotation='vertical')
    fig.text(0.5, 0.03, 'f (GHz)', ha='center')

def over(s, titles=('on', 'off')):
    figure(5);clf()
    fig, axes2d = subplots(num=5, nrows=5, ncols=1,
                           sharex=True, sharey=True,
                           figsize=(22,12))
    sind=s.d_on.getscanind()
    for i, cell in enumerate(axes2d):
        for j in (0, 1):
            on_or_off = (s.xon, s.xoff)[j]
            cell.set_ylabel(s.za[i+1])
            cell.yaxis.set_label_position("right")
            data = nanmean((on_or_off[s.d_on.za==s.za[i+1]].T\
                                -nanmean(on_or_off[s.d_on.za==s.za[i+1],700:1000],1)).T,0)
            cell.plot(s.f, data, color='br'[j], label=titles[j])
            cell.set_xlim(s.f[0], s.f[-1])
            cell.set_xticks(linspace(s.f[0], s.f[-1], 12))
            cell.set_xticklabels((round(a,1) for a in linspace(s.f[0], s.f[-1], 12) / 1e3), rotation='vertical')
            cell.set_ylim(-5, 5)
            cell.grid(True)
            if i == 2:
                cell.legend()
    fig.text(0.5, 0.97, 'Calibrated spectra\'s deviation from median ZA\'s, mean-subtracted and averaged over {} scans.'.format(s.d_on.nscan), ha='center', fontsize=15)
    fig.text(0.06, 0.5, 'T (K)', va='center', rotation='vertical')
    fig.text(0.94, 0.5, 'ZA (deg)', va='center', rotation='vertical')
    fig.text(0.5, 0.03, 'f (GHz)', ha='center')

def tseries(s, titles=('on', 'off')):
    figure(7);clf()
    
        
def main(s):
    tsys(s)
    tant(s)
    tcal(s)
    ims(s)

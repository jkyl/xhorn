from matplotlib.pyplot import *
from numpy import *
from scipy.interpolate import interp1d
import am_model as am
from scipy.constants import h,c,k
from scipy import loadtxt, optimize
import pylab as plt
from scipy.stats import norm

baffle_ = True
plot_1d_pattern = False
plot_2d_pattern = False

Sum = True
compare_groundpickup = False
I_spectrum = False
Tb_spectrum = True


za=90
zamin=0.
zamax=80.
dza=5.

elmin=-180.
elmax=180.
elN=2000

azmin=-90.
azmax=90.
azN=2000

gmin=9
gmax=12
dg=1

fmin=1
fmax=3000
df=.1

T=290

az=linspace(azmin,azmax,azN)
el=linspace(elmax,elmin,elN)
x,y=meshgrid(az,el)
r=sqrt(x**2 + y**2)
grange=arange(gmin,gmax+dg,dg)
frange=arange(fmin,fmax+df,df)
zarange=arange(zamin,zamax+dza,dza)

X, Y = loadtxt('xhorn_nobaffle.tsv', unpack=True, usecols=[0,1])
XX,YY= loadtxt('xhorn_baffle.tsv',unpack=True, usecols=[0,1])
nobaff=interp1d(X,Y,kind='linear')
baff=interp1d(XX,YY,kind='linear')

def fit(p,x):
    return exp(-x**2/(2*p**2))
def residual(p,x,y):
    return (fit(p,x)-y)/y
p0=1.
pf, cov, info, mesg, success = optimize.leastsq(residual, p0,
                           args=(zarange[zarange<=17], nobaff(zarange[zarange<=17])), full_output=1)

def I(f,T):
    return (2*h*(f*1e9)**3/c**2)*((exp(h*(f*1e9)/(k*T))-1)**-1)
p=am.readamcfile('SPole_winter.amc');p.pwv=500
q=am.am(prof=p,fmin=fmin,fmax=fmax,df=df*1e3)
cmap=get_cmap('hsv')
colors=[cmap(i) for i in linspace(0, 1, len(zarange))]

###########################
if plot_1d_pattern is True:
###########################
    if success>=4:
        print 'not converged'
    ax=axes()
    plot(zarange,10*log10(nobaff(zarange)),label='10GHz, no baffle')
    plot(zarange,10*log10(baff(zarange)),label='10GHz, baffle')
    plot(zarange,10*log10(fit(pf,zarange)),'--',label=r'Gaussian, FWHM $=%.4s^{\circ}$'%(2.355*pf[0]))
    legend(loc='best')
    xlabel('Degrees off-axis');ylabel('Gain (dBs)')
    ylim(-80,1)
    show();clf()

###########################
if plot_2d_pattern is True:
###########################
    imshow(10*log10(nobaff(r)),interpolation='nearest',extent=[azmin,azmax,elmax,elmin])
    colorbar();show()
    imshow(10*log10(baff(r)),interpolation='nearest',extent=[azmin,azmax,elmax,elmin])
    colorbar();show()
    ax=plt.subplot(111,projection='aitoff')
    ax.grid(True)
    ax.contourf(y*pi/180.,x*pi/180.,10*log10(((roll(baff(r),int(round((za-90)*elN/360.)),axis=0)))*(y<=0)))
    show()
    clf()

###############
if Sum is True:
###############
    baffresults=[]; nobaffresults=[];gaussresults=[]
    for za in zarange:
        baffresults.append(sum(roll(baff(r),int(round(elN*(za-90)/360.)),axis=0)*(y<=0))/sum(baff(r)))
        nobaffresults.append(sum(roll(nobaff(r),int(round((za-90)*elN/360.)),axis=0)*(y<=0))/sum(nobaff(r)))
        gaussresults.append(sum(roll(fit(pf,r),int(round((za-90)*elN/360.)),axis=0)*(y<=0))/sum(fit(pf,r)))

    ################################
    if compare_groundpickup is True:
    ################################
        plot(zarange,10*log10(baffresults),label='Baffle')
        plot(zarange,10*log10(nobaffresults),label='No baffle')
        plot(zarange,10*log10(gaussresults),'--',label=r'Gaussian, FWHM $=%.4s^{\circ}$'%(2.355*pf[0]))
        ylim(-52,1)
        xlabel('Zenith angle (deg)')
        ylabel('Ground pickup (dBs)')
        legend(loc='best')
        show()
        clf()

    ######################
    if I_spectrum is True:
    ######################
        loglog(frange,I(frange,T),'k',label=r'$%s\mathrm{K\, blackbody}$'%(T))
        for q.za in zarange:
            q.callam()
            q.parseresults()
            loglog(q.f,q.I,color=colors[int((zarange==q.za).nonzero()[0])],label=r'$\theta_z=%.4s^{\circ}$'%(q.za))
        if baffle_ is True:
            for n in baffresults:
                loglog(grange,n*I(grange,T),'--',linewidth=2,color=colors[int((baffresults==n).nonzero()[0])])
                title('Baffle')
        else:
            for n in nobaffresults:
                loglog(grange,n*I(grange,T),'--',linewidth=2,color=colors[int((nobaffresults==n).nonzero()[0])])
                title('No Baffle')
        legend(loc='best')
        xlabel(r'$f$   (GHz)')
        ylabel(r'Intensity ($W\cdot sr^{-1}\cdot Hz^{-1}\cdot m^2$)')
        xlim(5,1000)
        ylim(1e-23,1e-13)
        show()
        clf()

    #######################
    if Tb_spectrum is True:
    #######################
        loglog(frange,T*ones(len(frange)),'k',label=r'$%s\mathrm{K\,blackbody}$'%(T))
        for q.za in zarange:
            q.callam()
            q.parseresults()
            loglog(q.f,q.Tb,color=colors[int((zarange==q.za).nonzero()[0])],label=r'$\theta_z=%.4s^{\circ}$'%(q.za))
        if baffle_ is True:
            for n in baffresults:
                loglog(grange,n*T*ones(len(grange)),'--',linewidth=2,color=colors[int((baffresults==n).nonzero()[0])])
                title('Baffle')
        else: 
            for n in nobaffresults:
                loglog(grange,n*T*ones(len(grange)),'--',linewidth=2,color=colors[int((nobaffresults==n).nonzero()[0])])
                title('No baffle')
        legend(loc='best')
        xlabel(r'$f$   (GHz)')
        ylabel('Brightness temperature (K)')
        xlim(5,1000)
        ylim(1e-3,1e3)
        show()
        clf()

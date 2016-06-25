import in_out
import os
import numpy as np
from copy import deepcopy as dc
from IPython.core.debugger import Tracer; debug_here=Tracer()
import reduc_spec 
import am_model as am
import planck

def runsim():
    # Dummy trajectory
    d=reduc_spec.data((2016,06,17,23,27,41),(2016,06,18,0,0,0))

    # Sky model, only atmosphere and CMB (included as T0 param to am) for now
    sm=skymodel(comp=['atm'])

    # Signal only (in K)
    d=gensig().run(d,sm)

    # Add noise
    #d=addTrx(d,Trx=150)

    # Multiply by gain
    d=multgain(d)
    
    # Mock ambient temp cal stares
    d=makecal(d);

    # Add non-linearity
    d=addnonlin(d,0.001)

    # Fit gain and airmass
    d.fitam()

    return d

def getampath():
    return os.getenv('AM_PATH')

def gettraj():
    d=reduc_spec.data((2016,05,25,14,0,0),(2016,05,25,15,0,0))        
    return d
    
def za2am(za, type=None):
    """Compute airmass for given input tau. Zenith angle in degrees.
    type = 'secant' (default), 'Young'"""
    
    if type is None:
        type='secant'
        
    if type == 'secant':
        am=1/np.cos(za*np.pi/180)
            
    if type == 'Young':
        print 'Not coded yet'
            
    return am

def Iz2Iam(Iz,tauz,am):
    """Compute intensity as a function of airmass given zenith intensity and
    zenith optical depth."""
    I = Iz*(1-np.exp(-am*tauz))/(1-np.exp(-tauz))
    return I

class skymodel:

    def __init__(self,comp=['atm','recomb','cmb']):
        self.m={}
        self.genmodel(comp)
    
    def genmodel(self,comp):
        """Ideal sky model in T units (K)"""

        if 'atm' in comp:
            self.atm()
            
        if 'recomb' in comp:
            self.recomb()

        if 'cmb' in comp:
            self.cmb()
            
    def atm(self):
        # Atmospheric model
        p=am.readamcfile('{0}/generic/generic_mid.amc'.format(getampath()))

        # Total atm signal
        p.Nscale['h2o']=20.0/19.25 # nscale=1 is 19.25 mm pwv
        p.T0 = 2.7 # include CMB here
        self.m['atm']=p

    def recomb(self):
        # Recomb signal
        xx=np.loadtxt('recomb_spec/HI.HeI.HeII.dat');

        # Convert to K
        f=xx[:,0]*1000 # frequency in MHz
        I=xx[:,1] # W/m^2/Hz/sr
        T=planck.I2Ta(f*1e6,I).value
        self.m['sig']=np.vstack((f,T))

    def cmb(self):
        # CMB
        self.m['planck']=2.725


class gensig:

    def __init__(self):
        """Return simulated spectra"""


    def run(self,din,sm):

        # Copy
        d = dc(din)
        
        # Zero spec
        d.spec=np.zeros(d.spec.shape)

        model=sm.m
        nf=d.nf
        nt=d.t.size
        
        for k,mtype in enumerate(model):

            print mtype

            if isinstance(model[mtype],am.profile):
                # Atmosphere
                p=model[mtype]
                self.genatm(d,p,nf,nt)
                
            if mtype == 'sig':
                # Recombination line signal
                self.genrecomb(d,model[mtype])

            if mtype == 'planck':
                # Thermal CMB
                self.gencmb(d)

            if hasattr(model[mtype],'endswith'):
                # Sky map (not yet implemented)
                fname=m[mtype]
                self.genfromhmap(self,fname)

        # spec will be manipulated further, so store it
        d.Tsig = d.spec

        return d

    def genatm(self,d,p,nf,nt):
        """Generate airmass modulated atmospheric signal""" 

        v=np.zeros((nf,nt))
        
        df=d.f[2]-d.f[1]
        fmin=np.min(d.f)/1000
        fmax=np.max(d.f)/1000
        m=am.am(prof=p,df=20,fmin=fmin*0.9,fmax=fmax*1.1,za=0)
        m.callam()
        m.parseresults()
        
        airmass=za2am(d.za,'secant') # could use d.am
        T=np.interp(d.f,m.f*1000,m.Tb)
        
        # Can take into account non-linearit
        #for l,aml in enumerate(airmass):
        #    v[:,l]=self.Iz2Iam(m.I,m.tau,aml)
        # Just scale linearly with airmass, add complication later
        Tscale=T*np.tile(airmass,(d.nf,1)).T
        d.spec=d.spec+Tscale

    def genrecomb(self,d,m):
        """Generate constant recombination line signal"""
        y=np.interp(d.data.f,m.f,m.I)
        y=np.reshape(y,[y.size,1])
        v=np.tile(y,[1,nt])
        d.data.append(v,mtype)

    def gencmb(self,d):
        """Constant Planck curve for 2.725 blackbody"""
        I=(planck.planck(d.data.f*1e9, 2.725))
        v=np.tile(I.reshape(I.shape+(1,)),(1,nt))
        d.data.append(v,mtype)

    def genfromhmap(self,d,fname):
        """Interpolate input healpix map along scan trajectory. Need to make
        some assumption about frequency dependence. Not yet implemented"""
        # Input sky map, assume in galactic coords
        print(fname)

def addTrx(din,Trx=150):
    """Add nosie in K"""
    d=dc(din)
    fac=Trx/np.sqrt(d.acc_len*(d.f[1]-d.f[0])*1e6)
    n=fac*np.random.randn(d.t.size,d.nf)+Trx
    d.spec=d.spec+n
    d.nsim=n
    return d

def multgain(din):
    """Multiply by gain in V^2 / K"""
    d=dc(din)
    # Sine wave
    g = 1e6*(np.sin(d.f/100)+1.25);
    g = g*((9500-d.f)/3000 + 1)
    
    d.gsim=g
    d.spec=d.spec*np.tile(g,(d.spec.shape[0],1))
    return d

def makecal(din):
    """Mock cal scans"""
    d=dc(din)
    if hasattr(d,'nsim'):
        n=d.nsim
    else:
        n=np.zeros(d.spec.shape)
    
    d.spec[d.getcalind()]=(290+n[d.getcalind()])*d.gsim
    return d

def addnonlin(din,fac=0.01):
    """Add in non-linearity, fac is non-linearity
    as in V ~ T^(1+fac*randn(Nfreq))"""
    d=dc(din)
    beta=1+fac*np.random.randn(d.nf)
    d.beta=beta
    d.spec=d.spec**np.tile(beta,(d.t.size,1))
    return d

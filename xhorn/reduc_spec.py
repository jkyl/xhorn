import in_out
import numpy as np
from copy import deepcopy as dc
from IPython.core.debugger import Tracer; debug_here=Tracer()
from matplotlib.pyplot import *
import planck

# Useful trig functions
def asind(x):
    return np.arcsin(x)*180/np.pi
def sind(x):
    return np.sin(x*np.pi/180)
def cosd(x):
    return np.cos(x*np.pi/180)
def atand2(x,y):
    return np.arctan2(x,y)*180/np.pi

def arr(x):
    if type(x) is int:
        x=np.array([x])
    return x

def azel2radec(az,el,mjd,lat=47.8781,lon=-87.6298):
    """Convert az/del to ra/dec, Chicago lat/lon by default. Input/output in
    degrees."""
    
    T_UT1 = (mjd-51544.5)/36525;
    ThetaGMST = 67310.54841 + (876600*3600 + 8640184.812866)*T_UT1 + \
        .093104*(T_UT1**2) - (6.2e-6)*(T_UT1**3)
    ThetaGMST = np.mod((np.mod(ThetaGMST,86400*(ThetaGMST/np.abs(ThetaGMST)))/240),360)
    ThetaLST = ThetaGMST + lon
        
    DEC = asind(sind(el)*sind(lat)+cosd(el)*cosd(lat)*cosd(az))
    LHA = atand2(-sind(az)*cosd(el)/cosd(DEC), 
                  (sind(el)-sind(DEC)*sind(lat))/(cosd(DEC)*cosd(lat)))*(180/np.pi);
    RA = np.mod(ThetaLST-LHA,360);
    
    return RA,DEC

class data:

    def __init__(self, ts, tf):
        '''
        Read in data, t0 and t1 as tuples, e.g. (2016,5,3,0,0,0)
        '''
        
        # Read data
        d=in_out.read_time_range(dt_0=ts,dt_f=tf)
        
        # Modified Julian date
        self.mjd=d['mjd'][:,0]

        # Hours since beginning of read
        self.t=(self.mjd-self.mjd[0])*24; 

        # Sample rate in MHz
        if np.unique(d['samp_rate_mhz']).size > 1:
            raise NameError('Sample rate changed during accumulation')
        else:
            self.samp_rate = d['samp_rate_mhz'][0]
            
        # Accumulation length in s
        if np.unique(d['acc_len_secs']).size > 1:
            raise NameError('Accumulation length changed during accumulation')
        else:
            self.acc_len = d['acc_len_secs'][0]

        # spectrum data
        self.spec=d['spec'].astype(float)

        # mask data
        m=self.getmask()
        self.applymask(m)
        
        # Frequency axis
        self.f = np.linspace(0,self.samp_rate/2,self.spec.shape[1])

        # Add LO frequency
        self.f=self.f+9500

        # Zenith angle in degrees. 
        self.za=d['angle_degs']-d['zenith_degs']
        self.za=self.za[:,0]

        # Airmass
        self.am=self.za2am(self.za)

        # az/el -> RA/Dec
        az=120.0 # Hard coded to SE for now
        self.ra,self.dec=azel2radec(az,90-self.za,self.mjd) 

        # Get stepping/cal indices
        self._getscanind()

        # Useful information
        self.nscan=self.ind['ss'].size
        self.nf=self.f.size


        ##################
        # Do the reduction
        ##################
        #zarange=[20,50]
        #self.reduc(zarange)

    def za2am(self,x):
        """Zenith angle in degrees to airmass"""
        return 1/cosd(x)

        
    def reduc(self,zarange=[20,50]):
        """Main reduction script. Elrange is two element list or tuple over
        which to perform airmass regression (inclusive)"""
        
        # Convert P-> T RJ
        self.P2T()

        # First, take out a secular gain drift for each constant elevation
        # stare. Fit P(t) to each channel in a contiguous elevation stare,
        # normalize fit to mean=1, and normalize each chan to this.
        #deg=10
        #self.removedrift(deg)

        # Now fit a line to P(am) in each scan and store the results.
        self.fitam(zarange)

    def P2T(self):
        """Scale by P->TRJ factor"""
        # Convert to RJ temperature
        fac=planck.I2Ta(self.f*1e6,1).value
        fac=fac/fac[0]
        self.spec=self.spec*np.tile(fac,(self.spec.shape[0],1))
        
    def _getscanind(self):
        """Identify start/stop indices of cal and scanning"""
        
        # Cal zenith angle
        zacal = -80;

        # Calibration stare indices
        calind = np.where(self.za==zacal)[0]
        cs = calind[np.where((calind-np.roll(calind,1))!=1)[0]]
        ce = calind[np.where((np.roll(calind,-1)-calind)!=1)[0]]+1

        # Stepping indices
        calind = np.where(self.za!=zacal)[0]
        ss = calind[np.where((calind-np.roll(calind,1))!=1)[0]]
        se = calind[np.where((np.roll(calind,-1)-calind)!=1)[0]]+1
        
        self.ind={'cs':cs,'ce':ce,'ss':ss,'se':se}

        # Define a scan block array
        self.scan=np.zeros(self.spec.shape[0])
        for k,val in enumerate(ss):
            self.scan[cs[k]:se[k]]=k;

    def getind(self,start,end,blk):
        """Return indices corresponding to start and end indices, strings as
        defined in self.ind"""

        if blk is None:
            # Return all blocks
            blk = np.arange(self.ind[start].size)

        ind=np.array([])
        for k,val in enumerate(blk):
            ind=np.append(ind,np.arange(self.ind[start][val],self.ind[end][val]))
        return ind.astype(int)


    def getscanind(self,blk=None,zarange=[0,90]):
        """Return indices of periods of stepping. Scanblock goes from 0 to
        Nscans-1, and will return the indices of the scan blocks requested.
        Default is to return all scan blocks and all zenith angles."""
        ind=self.getind('ss','se',arr(blk))
        ind=ind[(self.za[ind]>=zarange[0]) & (self.za[ind]<=zarange[1])]
        return ind
    
    def getcalind(self,blk=None):
        """Return indices of periods of calibrator staring. If blk is defined,
        return all indices of cal stares, including leading and trailing for
        each block."""
        if blk!=None:
            blk=arr(blk)
            cblk=np.array([]).astype(int) # Initialize cal stare indices
            cs=self.ind['cs']
            ce=self.ind['ce']
            for k,val in enumerate(blk):
                ss=self.ind['ss'][val] # Scan start
                se=self.ind['se'][val] # Scan stop
                # Find leading cal stare 
                ind=np.where(ce<=ss)[0]
                if ind.size>0:
                    # If it exists, append it
                    cblk=np.append(cblk,ind[-1])

                # Find trailing cal stare 
                ind=np.where(cs>=se)[0]
                if ind.size>0:
                    # If it exists, append it
                    cblk=np.append(cblk,ind[0])
        else:
            cblk=None

        return np.unique(self.getind('cs','ce',blk=cblk))

    def calccalmean(self,blk):
        """Calculate mean of lead/trail cal stare for each scan block"""
        calind=self.getcalind(blk)
        x=self.spec[calind,:]
        return np.nanmean(x,axis=0)
            
    def getmask(self):
        """ Get NtxNf mask"""
        mask=np.ones(self.spec.shape)

        # Right now just make out DC and clock freq
        mask[:,1024]=0;
        mask[:,0]=0;

        return mask

    def applymask(self,mask):
        """Set spec values to 0 where mask is zero"""
        self.spec[mask==0]=np.nan

    def removedrift(self,deg=10):
        """Fit and remove a polynomial from P(t) for each frequency channel for
        a block of contiguous, constant elevation stares"""

        # First remove a secular zeropoint drift over the entire scanset. Fit just the
        # scans but remove from cal stares as well.
        x=self.t
        scanind=self.getscanind()
        for k in range(self.nf):
            y=self.spec[:,k]
            if not np.any(np.isnan(y)):
                p=np.polyfit(x[scanind],y[scanind],deg=deg)
                # Don't remove mean 
                p[-1]=0
                self.spec[:,k]=self.spec[:,k]-np.poly1d(p)(x)

        return
    
        for k in range(self.nscan):
            # Each scan
            ind=self.getscanind(k)

            for j,val in enumerate(np.unique(self.za[ind])):
                # Find contiguous blocks                
                doind=ind[np.where(self.za[ind]==val)]
                dx=doind-np.roll(doind,1)
                startind=np.where(dx!=1)[0]
                endind=np.append(startind[1:],dx.size)

                for l,val in enumerate(startind):
                    # For each contiguous block
                    s=doind[startind[l]]
                    e=doind[endind[l]-1]+1
                    x=self.t[s:e]
                    x=x-x.mean()
                    y=self.spec[s:e,:]

                    for m in range(self.nf):
                        # For each channel
                        yy=y[:,m];
                        if not np.any(np.isnan(yy)):
                            p=np.polyfit(x,yy,deg=deg); # Fit p3
                            z=np.poly1d(p)
                            yy=yy-z(x)
                            self.spec[s:e,m]=yy # replace data

                    
    def fitam(self,zarange=[20,50]):
        """Fit a line to P(am)"""
        
        # Loop over scan blocks and fit each 
        m=np.zeros([self.nscan,self.nf]) # slope of P(am) fit
        b=np.zeros([self.nscan,self.nf]) # intercept of P(am) fit
        g=np.zeros([self.nscan,self.nf]) # gain
        c=np.zeros([self.nscan,self.nf]) # mean of cal stare
        Trx=np.zeros([self.nscan,self.nf]) # noise temperature

        Th=290 # hot load
        Tz=20 # Zenith temperature
        Tiso=2.7

        for k in range(self.nscan):
            # Pull out scanning data for this block
            ind=self.getscanind(k)
            za=self.za[ind]
            am=self.am[ind]
            s=self.spec[ind,:]

            # Find where elevation is in range
            fitind=np.where((za>=zarange[0]) & (za<=zarange[1]))[0]
            x=am[fitind]
            y=s[fitind,:]
            
            # Fit P(am) for each frequency
            for j in range(self.nf):
                yy=y[:,j]
                if not np.any(np.isnan(yy)):
                    p=np.polyfit(x,yy,deg=1);
                    m[k,j]=p[0]
                    b[k,j]=p[1]

            # Try to get gain
            # Mean of lead/trail cal stare
            c[k,:] = self.calccalmean(k)
            g[k,:]=(c[k,:]-b[k,:])/(Th-Tz)

            # Noise temperature
            Trx0=np.linspace(0,500,1000);

            rhs = (Trx0+Th)/(Trx0+Tiso)
            for j in range(self.nf):
                Ph=c[k,j] # hot load
                Pc=b[k,j] # cold load
                lhs = Ph/Pc
                Trx[k,j]=np.interp(0,lhs-rhs,Trx0)

        self.c = c
        self.m = m
        self.b = b
        self.g = g
        self.Trx=Trx

    def expandcal(self):
        """Return an index array to expand an nscan x nf array of cal data to an array
        of size self.spec (nt x nf). 
        ex. ind=expandcal(); ratio=self.scan/self.c[ind]
        """
        ind=np.zeros(self.spec.shape[0]).astype(int)
        for k in range(self.nscan):
            ind[self.getscanind(k)]=k
            ind[self.getcalind(k)]=k
        return ind

    def svd(self):
        """SVD filter"""

        self.fspec=np.zeros(self.spec.shape)
        self.u=[]
        self.s=[]
        self.v=[]

        for k in range(self.nscan):
            sind=self.getscanind(k)
            x=self.spec[sind]
            x[np.isnan(x)]=0
            u,s,v=np.linalg.svd(x,full_matrices=True)
            ss=dc(s)
            ss[0]=0
            SS=np.zeros(x.shape)
            
            sz=x.shape[0]
            SS[:sz,:sz]=np.diag(ss);
            z=np.dot(u,np.dot(SS,v))
            
            #for k in range(sz):
            #    y=z[k];ind=np.arange(500,1000);p=np.polyfit(self.f[ind],y[ind],deg=3);
            #    z[k]=y-np.poly1d(p)(self.f);
            self.fspec[sind]=z
            self.u.append(u)
            self.s.append(s)
            self.v.append(v)

        return u,s,v,self.fspec

    def atmgaincal(self,flim=[10000,10500]):
        """Gain cal on atmosphere"""
        sind=self.getscanind()
        ind=self.expandcal()
        amm=np.tile(self.am,(self.nf,1)).T
        x=(self.spec-self.b[ind])/self.g[ind];x=x[sind]
        x=x/amm[sind]
        y=x[ np.where((self.za[sind]>=25) & (self.za[sind]<=35))[0] ]
        
        #for k in range(y.shape[0]):
        #    y[k]=y[k]-np.nanmedian(y[k])

        f=self.f+9500
        find=np.where((f>=flim[0]) & (f<=flim[1]))[0]
        
        for k in range(y.shape[0]):
            x=self.f[find];
            yy=y[k,find];
            p=np.polyfit(x,yy,deg=1);
            y[k]=y[k]-np.poly1d(p)(self.f)

        return y

    def wmean(self,y,flim=[10000,10500]):

        f=self.f+9500
        find=np.where((f>=flim[0]) & (f<=flim[1]))[0]
        w=np.tile(1/np.nanstd(y[:,find],axis=1)**2,(2048,1)).T;
        ym=np.sum(y*w,axis=0)/np.sum(w,axis=0)
        return ym


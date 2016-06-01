import in_out
import numpy as np
from matplotlib.pyplot import *

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
        self.mjd=d['mjd'] 

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
        self.spec=d['spec'] 

        # Frequency axis
        self.f = np.linspace(0,self.samp_rate/2,self.spec.shape[1])

        # Zenith angle in degrees. 
        self.za=d['angle_degs']-d['zenith_degs']
        self.za=self.za[:,0]

        # Airmass
        self.am=1/cosd(self.za)

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
        zarange=[20,35]
        self.reduc(zarange,)


    def reduc(self,zarange):
        """Main reduction script. Elrange is two element list or tuple over
        which to perform airmass regression (inclusive)"""

        # Loop over scan blocks and fit each 
        m=np.zeros([self.nscan,self.nf]) # slope of P(am) fit
        b=np.zeros([self.nscan,self.nf]) # intercept of P(am) fit
        g=np.zeros([self.nscan,self.nf]) # gain

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
                p=np.polyfit(x,yy,deg=1);
                m[k,j]=p[0]
                b[k,j]=p[1]

            # Try to get gain
            # Mean of lead/trail cal stare
            cm = self.calccalmean(k)
            g[k,:]=(cm-b[k,:])/(290-5)

        self.m = m
        self.b = b
        self.g = g

    def _getscanind(self):
        """Identify start/stop indices of cal and scanning"""
        
        # Cal zenith angle
        zacal = -70;

        # Calibration stare indices
        calind = np.where(self.za==zacal)[0]
        cs = calind[np.where((calind-np.roll(calind,1))!=1)[0]]
        ce = calind[np.where((np.roll(calind,-1)-calind)!=1)[0]]

        # Stepping indices
        calind = np.where(self.za!=zacal)[0]
        ss = calind[np.where((calind-np.roll(calind,1))!=1)[0]]
        se = calind[np.where((np.roll(calind,-1)-calind)!=1)[0]]

        self.ind={'cs':cs,'ce':ce,'ss':ss,'se':se}


    def getind(self,start,end,blk):
        """Return indices corresponding to start and end indicies, strings as
        defined in self.ind"""

        if blk == None:
            # Return all blocks
            blk = np.arange(self.ind[start].size)

        ind=np.array([])
        for k,val in enumerate(blk):
            ind=np.append(ind,np.arange(self.ind[start][val],self.ind[end][val]+1))
        return ind.astype(int)


    def getscanind(self,blk=None):
        """Return indices of periods of stepping. Scanblock goes from 0 to
        Nscans-1, and will return the indices of the scan blocks requested.
        Default is to return all scan blocks."""
        return self.getind('ss','se',arr(blk))


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
                ind=np.where(ce<ss)[0]
                if ind.size>0:
                    # If it exists, append it
                    cblk=np.append(cblk,ind[-1])

                # Find trailing cal stare 
                ind=np.where(cs>se)[0]
                if ind.size>0:
                    # If it exists, append it
                    cblk=np.append(cblk,ind[0])
        else:
            cblk=None

        return np.unique(self.getind('cs','ce',blk=cblk))

    def calccalmean(self,blk):
        """Calculate mean of lead/trail cal stare for each scan block"""
        calind=self.getcalind(blk)
        return self.spec[calind,:].mean(axis=0)
            

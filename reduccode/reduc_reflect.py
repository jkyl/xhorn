from numpy import *
from scipy.interpolate import *
from matplotlib.pyplot import *



# Received powers with rectangular horn (ADU^2)
Prx=array([1e10,8e10,1e9,2e10,9e8,7e10,1e11,1e10,3e10,0,1e10,6e9,0]) # No lid
#Prx=array([3e9,8e9,1e9,2e9,3e7,3e10,3e9,1e10,3e9,0,0,6e8,6e8])

# Signal generator power
Pout=array([10.,10,-20,0,0,0,0,0,0,0,0,0,0])

# Lat/lon of measurement
x = array([-90., -45,   0,  45,  90,   0,   0,  0,   0, 180, -135, 135, 180])
y = array([-20., -20, -20, -20, -20,  45, -45, 90, -90,   0,    0,   0,  45])


# Interpolate to lat/lon grid
yi=linspace(-90,90,100)
xi=linspace(-180,180,100)
xx,yy=meshgrid(xi,yi)

# Convert measured powers to power / Area at reference output power of 0 dBm
Ahorn = 18.125 # Measured rectangular horn aperture area in in^2
P = Prx / 10**(Pout/10) / Ahorn # ADU^2 / in^2

# Interpoalate onto lat/lon grid
# First mirror data to enforce periodicity on sphere
xm=concatenate((x-360,x,x+360))
ym=concatenate((y,y,y))
Pm=concatenate((P,P,P))

#f = interp2d(x,y,P,kind='linear')
#Pi = f(xx,yy)
Pi = griddata((xm,ym),Pm,(xx,yy),method='cubic')
Pi[Pi<0]=0


clf();
imshow(Pi,extent=[xi[0],xi[-1],yi[-1],yi[0]]);
gca().invert_yaxis()
colorbar();
xlabel('lon');ylabel('lat')
title('ADU^2 / in^2 at 17" radius')

# Do numeric integral in spherical coordinates
r=17.0
dx=xi[1]-xi[0]
dy=yi[1]-yi[0]

Pint = r**2 * sum(Pi*cos(yy*pi/180)*(dx*pi/180)*(dy*pi/180))

# Total power expected
Ptot = 2e10 * 1e8 * 1.3

# Total reflected power in dB
R = 10*log10(Pint / Ptot)

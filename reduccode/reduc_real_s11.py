from numpy import *
from matplotlib.pyplot import *
from copy import deepcopy as dc

def getwin(n,s,e):
    w=np.zeros(n)
    nh=e-s
    w[s:e]=hamming(nh)

    return w

def gets11(fn):
    caldir='calibration/Traces/'
    x=loadtxt(caldir+fn,skiprows=3,delimiter=',',usecols=(0,1))
    v=10**(x[:,1]/10)

    # zero pad
    v=append(v,np.zeros(2048))

    f=x[:,0]
    df=(f[2]-f[1])
    tmax=1/(2*df)
    t=linspace(-tmax,tmax,v.size)

    # Only take 9-12 GHz
    fmin=10e9
    fmax=11e9
    s=where(abs(f-fmin)==min(abs(f-fmin)))[0]
    e=where(abs(f-fmax)==min(abs(f-fmax)))[0]
    w=getwin(v.size,s,e)

    v=v*w


    

    ft=fft.fftshift(fft.fft(v))

    return v,ft,f,t



###################
# Get attenuator calibration data
v_metal,ft_metal,f,t=gets11('s11_metal.csv')
v_vhp,ft_vhp,f,t=gets11('s11_vhp.csv')
v_crv,ft_crv,f,t=gets11('s11_crv.csv')


clf();
semilogy(t,abs(ft_metal),'.-')
semilogy(t,abs(ft_vhp),'.-')
semilogy(t,abs(ft_crv),'.-')
legend(['metal','vhp','crv'])

# Time domain window
tmin=3e-9
tmax=5.5e-9
xlim(tmin,tmax)

s=where(abs(t-tmin)==min(abs(t-tmin)))[0]
e=where(abs(t-tmax)==min(abs(t-tmax)))[0]
w=getwin(t.size,s,e)
ft_metal=ft_metal*w
ft_vhp=ft_vhp*w
ft_crv=ft_crv*w


vf_metal=fft.ifft(fft.fftshift(ft_metal))
vf_vhp=fft.ifft(fft.fftshift(ft_vhp))
vf_crv=fft.ifft(fft.fftshift(ft_crv))

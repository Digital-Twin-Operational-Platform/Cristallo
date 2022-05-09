"""
# Generate modal data for 3DOF system using numerical integration
# DJW 26 December 2021
# 
# Currently this is for simulating an impact hammer excitation of a 3DOF (non)linear mass-spring system
# The impact force is applied to Mass 1, and random initial conditions are also applied to the displacements
# The parameters are ICs are selected from Gaussian distributions at the start of each time series simulation.
# The mean and standard deviations for the Gaussians can be defined in the code.
# 
# The results for N sets of displacement time series are put into the numpy array xs.
# Plots are produced to give a visual check.
"""

import numpy
from matplotlib import pyplot
from scipy import stats
from scipy.signal import savgol_filter

M_INP_1, M_INP_2, M_INP_3 = 5.0394,4.9919,4.9693
K_INP_1, K_INP_2, K_INP_3 = 34958.3691,43195.1237,43295.9086
C_INP_1, C_INP_2, C_INP_3 = 7.8963,4.0129,5.4905

M=[M_INP_1,M_INP_2,M_INP_3]
K=[K_INP_1,K_INP_2,K_INP_3]
C=[C_INP_1,C_INP_2,C_INP_3]
# ------------------ #
# INPUT DECLARATIONS
# ------------------ #
class MASS():
    def __repr__(self): # return
        return "[%f, %f, %f] %s"%(self.__m1,self.__m2,self.__m3,self.units)  
    def __str__(self): # print
        return "[%f, %f, %f] %s"%(self.__m1,self.__m2,self.__m3,self.units) 
    def __init__(self, x=[5.0, 5.0, 5.0], dispersion=.5, distribution='normal'):
        self.__m1 = x[0]
        self.__m2 = x[1]
        self.__m3 = x[2]
        self.__m = x
        self.__s = dispersion
        self.__dist = distribution
        self.units = 'kg'
    def value(self):
        return numpy.asarray(self.__m, dtype=float)
    def dispersion(self):
        return self.__s
    def distribution(self):
        if self.__dist == 'normal':
            return stats.norm(loc=self.__m, scale=3*[self.__s])
    def sample(self,N=10,seed=None):
        if seed is not None:
            numpy.random.seed(seed)
        dist = self.distribution()
        return dist.rvs((N,3)) # return numpy.random.normal(loc = self.__m, scale = 3*[self.__s])

class STIFF():
    def __repr__(self): # return
        return "[%f, %f, %f] %s"%(self.__k1,self.__k2,self.__k3,self.units)  
    def __str__(self): # print
        return "[%f, %f, %f] %s"%(self.__k1,self.__k2,self.__k3,self.units) 
    def __init__(self, x=[35025.0, 43250.0, 43250.0], dispersion=10.0, distribution='normal'):
        self.__k1 = x[0]
        self.__k2 = x[1]
        self.__k3 = x[2]
        self.__k = x
        self.__s = dispersion
        self.__dist = distribution
        self.units = 'N/m'
    def value(self):
        return numpy.asarray(self.__k, dtype=float)
    def dispersion(self):
        return self.__s
    def distribution(self):
        if self.__dist == 'normal':
            return stats.norm(loc=self.__k, scale=3*[self.__s])
    def sample(self,N=10,seed=None):
        if seed is not None:
            numpy.random.seed(seed)
        dist = self.distribution()
        return dist.rvs((N,3)) # return numpy.random.normal(loc = self.__m, scale = 3*[self.__s])
    
class DAMP():
    def __repr__(self): # return
        return "[%f, %f, %f] %s"%(self.__c1,self.__c2,self.__c3,self.units)  
    def __str__(self): # print
        return "[%f, %f, %f] %s"%(self.__c1,self.__c2,self.__c3,self.units) 
    def __init__(self, x=[8.0, 8.0, 8.0], dispersion=1.0, distribution='normal'):
        self.__c1 = x[0]
        self.__c2 = x[1]
        self.__c3 = x[2]
        self.__c = x
        self.__s = dispersion
        self.__dist = distribution
        self.units = 'Ns/m'
    def value(self):
        return numpy.asarray(self.__c, dtype=float)
    def dispersion(self):
        return self.__s
    def distribution(self):
        if self.__dist == 'normal':
            return stats.norm(loc=self.__c, scale=3*[self.__s])
    def sample(self,N=10,seed=None):
        if seed is not None:
            numpy.random.seed(seed)
        dist = self.distribution()
        return dist.rvs((N,3)) # return numpy.random.normal(loc = self.__m, scale = 3*[self.__s])
    
class INIT():
    def __repr__(self): # return
        return "[%f, %f, %f] %s; [%f, %f, %f] %s"%(self.__x1,self.__x2,self.__x3,self.unit1,self.__v1,self.__v2,self.__v3,self.unit2)  
    def __str__(self): # print
        return "[%f, %f, %f] %s; [%f, %f, %f] %s"%(self.__x1,self.__x2,self.__x3,self.unit1,self.__v1,self.__v2,self.__v3,self.unit2) 
    def __init__(self, x=[0.01, 0.02, -0.01], v=3*[0], dispersion=[0.001,0], distribution='normal'):
        self.__x1 = x[0]
        self.__x2 = x[1]
        self.__x3 = x[2]
        self.__v1 = v[0]
        self.__v2 = v[1]
        self.__v3 = v[2]
        self.__x = x
        self.__v = v
        self.__s1 = dispersion[0]
        self.__s2 = dispersion[1]
        self.__dist = distribution
        self.unit1 = 'm'
        self.unit2 = 'm/s'
    def value(self):
        return numpy.asarray(self.__x+self.__v, dtype=float)
    def dispersion(self):
        return [self.__s1, self.__s2]
    def distribution(self):
        if self.__dist == 'normal':
            return stats.norm(loc=self.value(), scale=3*[self.__s1]+3*[self.__s2])
    def sample(self,N=10,seed=None):
        if seed is not None:
            numpy.random.seed(seed)
        dist = self.distribution()
        return dist.rvs((N,6)) # return numpy.random.normal(loc = self.__m, scale = 3*[self.__s])
    

class BETA():
    def __repr__(self): # return
        return "[%f, %f, %f] %s"%(self.__b1,self.__b2,self.__b3,self.units)  
    def __str__(self): # print
        return "[%f, %f, %f] %s"%(self.__b1,self.__b2,self.__b3,self.units) 
    def __init__(self, x=[0.0, 0.0, 0.0], dispersion=0.0, distribution='normal'):
        self.__b1 = x[0]
        self.__b2 = x[1]
        self.__b3 = x[2]
        self.__b = x
        self.__s = dispersion
        self.__dist = distribution
        self.units = 'units'
    def value(self):
        return numpy.asarray(self.__b, dtype=float)
    def dispersion(self):
        return self.__s
    def distribution(self):
        if self.__dist == 'normal':
            return stats.norm(loc=self.__b, scale=3*[self.__s])
    def sample(self,N=10,seed=None):
        if seed is not None:
            numpy.random.seed(seed)
        dist = self.distribution()
        return dist.rvs((N,3)) # return numpy.random.normal(loc = self.__m, scale = 3*[self.__s])

class HFORCE():
    def __repr__(self): # return
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __str__(self): # print
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __init__(self,x=300.0,at_time=0.5,duration=0.05,kind="Hammer"):
        self.__amp = x
        self.__dur = duration
        self.__att = at_time
        self.__kind= kind
        self.units = "N"
    def value(self,t=None):
        if t is None: t = self.__att
        else: t = numpy.asarray(t,dtype=float)
        return self.__amp * numpy.exp(-numpy.power(t - self.__att, 2.) / (2 * numpy.power(self.__dur, 2.)))
    def toplot(self,N=30,s=5):
        t = numpy.linspace(self.__att-s*self.__dur,self.__att+s*self.__dur, num=N)
        x = self.value(t=t)
        return t,x
class WFORCE():
    def __repr__(self): # return
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __str__(self): # print
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __init__(self,x=10.0,at_time=0.05,duration=10,kind="White Noise"):
        self.__amp = x
        self.__dur = duration
        self.__att = at_time
        self.__kind= kind
        self.units = "N"
        fs = 1000
        Ni = int(self.__dur*fs)
        A = numpy.ones(Ni)-numpy.floor(numpy.random.rand(Ni)*2)*2
        ps_rand_in = numpy.fft.irfft(Ni*A,Ni)
        ts = numpy.arange(0,Ni/fs,1/fs)    
        filtered = savgol_filter(ps_rand_in,7,5)
        filtered = filtered/numpy.max(filtered)
        self.filter = filtered
        self.timeInt = ts
    def value(self,t=None):
        if t is None: t = self.__att
        else: t = numpy.asarray(t,dtype=float)
        # return self.__amp * (0.42 * numpy.cos( 7 * t - 4) + 0.69 * numpy.cos(21 * t-1.1) + 0.7 * numpy.cos(37 * t - 2.3) + 0.6 * numpy.cos(78 * t - 1.9) + 0.5 * numpy.cos(96 * t - 3.5) + 0.4 * numpy.cos(117 * t - 2.9) + 0.5 * numpy.cos(156 * t - 3.1))
        return self.__amp*numpy.interp(t,self.timeInt,self.filter)       
    def toplot(self,N=30,s=5):
        t = numpy.linspace(self.__att-s*self.__dur,self.__att+s*self.__dur, num=N)
        x = self.value(t=t)
        return t,x
    
# ------------------- #
#      SIMULATOR      #
# ------------------- #
from scipy.integrate import odeint
def simulator(Defaults):
    N,t_length,t_samps=Defaults["N"],Defaults["T"],Defaults["S"]
    Mi,Ki,Ci,Ex=Defaults["M"],Defaults["K"],Defaults["C"],Defaults["Excite"]
    Xi,Vi,disp,d_init=Defaults["Ix"],Defaults["Iv"],Defaults["Disp"],Defaults["D_init"]
    
# def simulator(N = 30, t_length=10, t_samps=1000,Ex='Hammer',Mi=M,Ki=K,Ci=C,Xi=[0,0,0],Vi=[0,0,0],disp=[0,0,0],d_init=[0,0]):
    # This function defines the ODEs for the 3DOF system 
    def derivs(X, t):
        # Here X is the state vector such that x1=X[0] and xdot1=X[N-1]. 
        # This function should return [x1dot,...xNdot, xdotdot1,...xdotdotN]
        x1, x2, x3, xdot1, xdot2, xdot3 = X
        # compute ODE values
        xdotdot1 = -(c[0] / m[0]) * (xdot1) -(c[1] / m[0]) * (xdot1 - xdot2) -(k[0] / m[0]) * x1 -(k[1] / m[0]) * (x1 - x2) -(b[0] / m[0]) * (x1 - x2) * (x1 - x2) * (x1 - x2) + f.value(t=t) / m[0] #(FORCEAMP/ MASS[0])*np.exp(-np.power(t - mu, 2) / (2 * np.power(sig, 2)))
        xdotdot2 = -(c[1] / m[1]) * (xdot2 - xdot1) -(c[2] / m[1]) * (xdot2 - xdot3) -(k[1] / m[1]) * (x2 - x1) -(k[2] / m[1]) * (x2 - x3)-(b[1] / m[1]) * (x2 - x1) * (x2 - x1) * (x2 - x1)-(b[2] / m[1]) * (x2 - x3) * (x2 - x3) * (x2 - x3) 
        xdotdot3 = -(c[2] / m[2]) * (xdot3 - xdot2) -(k[2] / m[2]) * (x3 - x2) -(b[2] / m[2]) * (x3 - x2) * (x3 - x2) * (x3 - x2) 
        return [xdot1, xdot2, xdot3, xdotdot1, xdotdot2, xdotdot3]
    # define the time base parameters for the ODE integration
    ts = numpy.linspace(0, t_length, t_samps) 
    xs = numpy.zeros((N, 5, t_samps), float)
    # generate random samples
    M = MASS(Mi,dispersion=disp[0]).sample(N=N,seed=10) # MASS=np.random.normal(loc = MASSm, scale = MASSs)
    K = STIFF(Ki,dispersion=disp[1]).sample(N=N,seed=10) # STIFF=np.random.normal(loc = STIFFm, scale = STIFFs)
    B = BETA().sample(N=N,seed=10) # BETA=np.random.normal(loc = BETAm, scale = BETAs)
    C = DAMP(Ci,dispersion=disp[2]).sample(N=N,seed=10) # DAMP=np.random.normal(loc = DAMPm, scale = DAMPs)
    I = INIT(x=Xi,v=Vi,dispersion=d_init).sample(N=N,seed=10) # Init0=np.random.normal(loc = X0m, scale = X0s)
    if Ex=='Hammer':
        f = HFORCE(duration=1e-2)
    elif Ex=='White':
        f = WFORCE(50,duration=t_length)
    else:
        raise(Exception('Unknown Input'))
    # Check for Validity
    M[numpy.where(M<=0.0)]=0.1
    K[numpy.where(K<=0.0)]=0.1
    C[numpy.where(C<=0.0)]=0.1
    for i in range(N):
        m,k,b,c,init0 = M[i],K[i],B[i],C[i],I[i]
        Xs = odeint(derivs, init0, ts)
        # extract the displacements from the return vector
        xs[i,:,:]= [ts, Xs[:,0], Xs[:,1], Xs[:,2],f.value(t=ts)]
    return ts, xs

# ------------------- #
#      FOURIER T      #
# ------------------- #
from scipy import signal
def fourier_transform(t,x):
    N = x.shape[0]
    time_step=t[1]
    # Compute the power spectrum of the diplacement signals
    FF = 1/time_step
    ftemp, Pxx_temp = signal.welch(x[0, 1, :], FF, 'hann',256, scaling='density')
    freq = numpy.zeros((N, 3, ftemp.size), float)
    Pxx_spec = numpy.zeros((N, 3, Pxx_temp.size), float)
    for i in range(0, N):
        freq[i,0,:], Pxx_spec[i,0,:] = signal.welch(x[i, 1, :], FF, 'hann', 256, scaling='density')
        freq[i,1,:], Pxx_spec[i,1,:] = signal.welch(x[i, 2, :], FF, 'hann', 256, scaling='density')
        freq[i,2,:], Pxx_spec[i,2,:] = signal.welch(x[i, 3, :], FF, 'hann', 256, scaling='density')
    return freq, Pxx_spec

# if __name__ == '__main__':
#     tt,xx = simulator(Defaults)
#     # tt,xx = simulator(N=1,t_length=30,t_samps=int(30*8e4),Ex='Hammer',Mi=M,Ki=K,Ci=C,Xi=[0,0,0],Vi=[0,0,0],disp=[0,0,0],d_init=[0,0])
#     fr,Pxx = fourier_transform(tt,xx)
#     plot(tt,xx,fr,Pxx)
#     pyplot.show()
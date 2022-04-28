'''

`dtLib/threedof.py`


:Authors: 
    David J Wagg, University of Sheffield
    Marco De Angelis, University of Liverpool
    

:Created: December 2021
:Edited:  January 2022


:Copyright: 
    BSD Licence



This python file ``threedof.py`` is the scientific code for the simulator page.

This module is intended to be self-contained, thus it is orthogonal to any other scientific module in this software. 
It generates modal data for 3DOF system using numerical integration

 
Currently this is for simulating an impact hammer excitation of a 3DOF (non)linear mass-spring system
The impact force is applied to Mass 1, and random initial conditions are also applied to the displacements
The parameters are ICs are selected from Gaussian distributions at the start of each time series simulation.
The mean and standard deviations for the Gaussians can be defined in the code.

The results for N sets of displacement time series are put into the numpy array xs.
Plots are produced to give a visual check.

If inputs are not passed to the functions of this module the following default values will be assumed:

.. code-block:: python

    MASS = [5.0, 5.0,  5.0]            # kg

    STFF = [35025.0, 43250.0, 43250.0] # N/m

    DAMP = [8.0, 8.0, 8.0]             # Ns/m


This page makes use of the following dependencies.

External dependencies 

.. code-block:: python

    import numpy
    import numpy.integrate.odeint
    import scipy.stats
    import scipy.signal


If not otherwise specified: 

|    * The excitation is applied at floor 1. 
|    * The number of MonteCarlo samples is 30.
'''

import numpy
from scipy import stats

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
    def __init__(self, x=[0., 0.02, -0.01], v=3*[0], dispersion=[0.001,0], distribution='normal'):
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

class FORCE():
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
    
# ------------------- #
#      SIMULATOR      #
# ------------------- #
from scipy.integrate import odeint
def simulator(N = 30, t_length=10, t_samps=1000):
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
    time_step = t_length/t_samps
    ts = numpy.linspace(0, t_length, t_samps) 
    # now generate the sets of N time series
    # N = 100
    xs = numpy.zeros((N, 4, t_samps), float)
#     for i in range(N):
        # generate random samples
    M = MASS().sample(N=N,seed=10) # MASS=np.random.normal(loc = MASSm, scale = MASSs)
    K = STIFF().sample(N=N,seed=10) # STIFF=np.random.normal(loc = STIFFm, scale = STIFFs)
    B = BETA().sample(N=N,seed=10) # BETA=np.random.normal(loc = BETAm, scale = BETAs)
    C = DAMP().sample(N=N,seed=10) # DAMP=np.random.normal(loc = DAMPm, scale = DAMPs)
    I = INIT().sample(N=N,seed=10) # Init0=np.random.normal(loc = X0m, scale = X0s)
    f = FORCE()
    for i in range(N):
        m,k,b,c,init0 = M[i],K[i],B[i],C[i],I[i]
        Xs = odeint(derivs, init0, ts)
        # extract the displacements from the return vector
        xs[i,:,:]= [ts, Xs[:,0], Xs[:,1], Xs[:,2]]
    return ts, xs

# ------------------- #
#      FOURIER T      #
# ------------------- #
from scipy import signal
def fourier_transform(t,x):
    # t.shape = (1000,) # x.shape = (N,4,1000)
    N = x.shape[0]
    time_step=t[1]
    # Compute the power spectrum of the diplacement signals
    FF = 1/time_step
    ftemp, Pxx_temp = signal.welch(x[0, 1, :], FF, 'hann', 256, scaling='density')
    freq = numpy.zeros((N, 3, ftemp.size), float)
    Pxx_spec = numpy.zeros((N, 3, Pxx_temp.size), float)
    for i in range(0, N):
        freq[i,0,:], Pxx_spec[i,0,:] = signal.welch(x[i, 1, :], FF, 'hann', 256, scaling='density')
        freq[i,1,:], Pxx_spec[i,1,:] = signal.welch(x[i, 2, :], FF, 'hann', 256, scaling='density')
        freq[i,2,:], Pxx_spec[i,2,:] = signal.welch(x[i, 3, :], FF, 'hann', 256, scaling='density')
    return freq, Pxx_spec
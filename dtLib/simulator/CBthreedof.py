"""

`dtLib/threedof.py`

:Authors: 

    David J Wagg, University of Sheffield

    Marco De Angelis, University of Liverpool

    Matthew Bonney, University of Sheffield
    
:Created: December 2021
:Edited:  September 2022
:Copyright:     BSD Licence


This python file ``CBthreedof.py`` is the scientific code for the simulator page using the class based structure.

This module is intended to be self-contained, thus it is orthogonal to any other scientific module in this software. 
It generates modal data for 3DOF system using numerical integration
 
Currently this is for simulating an impact hammer excitation of a 3DOF (non)linear mass-spring system.

The impact force is applied to Mass 1, and random initial conditions are also applied to the displacements.

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

"""

import numpy as np
from scipy import stats
from scipy.integrate import odeint
from scipy.signal import savgol_filter
from dtLib import classes

class HFORCE():
    def __repr__(self): # return
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __str__(self): # print
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __init__(self,amp=300.0,at_time=0.5,duration=0.05,units="N"):
        self.__amp = amp
        self.__dur = duration
        self.__att = at_time
        self.units = units
    def value(self,t=None):
        if t is None: t = self.__att
        else: t = np.asarray(t,dtype=float)
        return self.__amp * np.exp(-np.power(t - self.__att, 2.) / (2 * np.power(self.__dur, 2.)))
    def toplot(self,N=30,s=5):
        t = np.linspace(self.__att-s*self.__dur,self.__att+s*self.__dur, num=N)
        x = self.value(t=t)
        return t,x
class WFORCE():
    def __repr__(self): # return
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __str__(self): # print
        return "%s: %f %s"%(self.__kind,self.__amp,self.units)  
    def __init__(self,amp=10.0,duration=10,units="N",fs=1048):
        self.__amp = amp
        self.__dur = duration
        self.units = units
        self.__fs = fs
        Ni = int(self.__dur*self.__fs)
        A = np.ones(Ni)-np.floor(np.random.rand(Ni)*2)*2
        th_rand_in = np.fft.irfft(Ni*A,Ni)
        ts = np.arange(0,Ni/fs,1/fs)    
        filtered = savgol_filter(th_rand_in,7,5)
        filtered = filtered/np.max(filtered)
        self.filter = filtered
        self.timeInt = ts
    def value(self,t):
        t = np.asarray(t,dtype=float)
        return self.__amp*np.interp(t,self.timeInt,self.filter)       

class INIT():
    def __repr__(self): # return
        return "[%f, %f, %f] %s; [%f, %f, %f] %s"%(self.__x1,self.__x2,self.__x3,self.unit1,self.__v1,self.__v2,self.__v3,self.unit2)  
    def __str__(self): # print
        return "[%f, %f, %f] %s; [%f, %f, %f] %s"%(self.__x1,self.__x2,self.__x3,self.unit1,self.__v1,self.__v2,self.__v3,self.unit2) 
    def __init__(self, x=[0.01, 0.02, -0.01], v=3*[0], dispersion=[0.001,0], distribution='normal',x_unit = "m", v_unit = "m/s"):
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
        self.unit1 = x_unit
        self.unit2 = v_unit
    def value(self):
        return np.asarray(self.__x+self.__v, dtype=float)
    def dispersion(self):
        return [self.__s1, self.__s2]
    def distribution(self):
        if self.__dist == 'normal':
            return stats.norm(loc=self.value(), scale=3*[self.__s1]+3*[self.__s2])
    def sample(self,N=10,seed=None):
        if seed is not None:
            np.random.seed(seed)
        dist = self.distribution()
        return dist.rvs((N,6)) 

def CBsimulator(model:classes.MODEL3DOF, param:dict):
    N,t_length,t_samps=param["N"],param["T"],param["S"]
    def derivs(X, t, m, k, c):
        # Here X is the state vector such that x1=X[0] and xdot1=X[N-1]. 
        # This function should return [x1dot,...xNdot, xdotdot1,...xdotdotN]
        x1, x2, x3, xdot1, xdot2, xdot3 = X
        # compute ODE values
        xdotdot1 = -(c[0] / m[0]) * (xdot1) -(c[1] / m[0]) * (xdot1 - xdot2) -(k[0] / m[0]) * x1 -(k[1] / m[0]) * (x1 - x2) + f.value(t=t) / m[0] 
        xdotdot2 = -(c[1] / m[1]) * (xdot2 - xdot1) -(c[2] / m[1]) * (xdot2 - xdot3) -(k[1] / m[1]) * (x2 - x1) -(k[2] / m[1]) * (x2 - x3)
        xdotdot3 = -(c[2] / m[2]) * (xdot3 - xdot2) -(k[2] / m[2]) * (x3 - x2) 
        return [xdot1, xdot2, xdot3, xdotdot1, xdotdot2, xdotdot3]
    # Setup time history
    ts = np.linspace(0, t_length, t_samps)
    xs = []
    # Setup Forcing
    if param["Excite"]=='Hammer':
        f = HFORCE(amp=300,units="N",at_time=0.5,duration=1e-2)
    elif param["Excite"]=='White':
        f = WFORCE(amp=50.0,duration=t_length,units="N",fs=1048)
    else:
        raise(Exception('Unknown Input'))
    # Initial conditions
    I0 = INIT(x=param["Ix"],v=param["Iv"],dispersion=param["D_init"])
    # Loop through sampling
    for i in range(N):
        m,k,c=model.sample(N=1) # resample each time / can be later changed to pre-rendered
        m,k,c = m.flatten(),k.flatten(),c.flatten()
        # Integrate
        Xs = odeint(func=derivs, y0=I0.sample(1).flatten(), t=ts, args=(m,k,c)) # resample each time / can be later changed to pre-rendered
        # Create Time History Object
        T1 = classes.TimeHistory(t=ts,t_u="seconds",x=Xs[:,0],x_u="m",source="Simulated")
        T2 = classes.TimeHistory(t=ts,t_u="seconds",x=Xs[:,1],x_u="m",source="Simulated")
        T3 = classes.TimeHistory(t=ts,t_u="seconds",x=Xs[:,2],x_u="m",source="Simulated")
        F = classes.TimeHistory(t=ts,t_u="seconds",x=f.value(t=ts),x_u=f.units,source="Simulated")
        xs.append([T1,T2,T3,F])
    return(xs)
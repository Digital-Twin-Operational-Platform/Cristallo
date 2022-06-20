from numpy import exp, power, log10, sqrt, abs, pi, argmax, asarray, arange, zeros
from scipy.integrate import odeint
from scipy import signal
from scipy.fft import fft
# from matplotlib import pyplot

# \\\\\\\\\\\\\\
# Default values

M = 1 # [kg] Mass
K = 10000 # [Ns] Stiffness
C = 2 # [Ns2]  Damping

DISP_init = 0   # Initial displacement
VELO_init = 0   # Initial velocity
INIT = [DISP_init,VELO_init]

F = 3   # Intensity of impact force
T = 4 # [s] observation time

# INTEGRATOR_STEPS = 1024
STEP_SIZE = 0.0001 # [s] 

DURATION = 0.01 # [s]
AT = 0.05 # [s]

GRID = True

DATA={
    'M': M,
    'K': K,
    'C': C,
    'DISP_init': DISP_init,
    'VELO_init': VELO_init,
    'F': F,
    'T': T,
    'STEP_SIZE':STEP_SIZE,
    'DURATION': DURATION,
    'AT': AT

}

# \\\\\\\\\\\\\\

def impulse(t:float,duration:float, attime:float):
    """
    :duration: duration of exerted impulse
    :attime:   time at which exertion starts
    """
    return exp(-power(t - attime, 2.) / (2 * power(duration, 2.)))

# simulator
def msd_simulator(data:dict=None): # https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html
    if data is None: data = DATA
    def derivs(y, t):
        # u,v = y
        x, xdot = y
        xdotdot = - data['C']/data['M']*xdot - data['K']/data['M'] * x + data['F']/data['M'] * impulse(t,data['DURATION'],data['AT']) 
        return [xdot, xdotdot]
    # t = linspace(0,T,num=INTEGRATOR_STEPS)
    t = arange(0,data['T'],step=data['STEP_SIZE'])
    xsol = odeint(derivs, [data['DISP_init'],data['VELO_init']], t)
    return t, xsol , data['F']/data['M'] * impulse(t,data['DURATION'],data['AT']) 

def fourier_transform(t,x,data):
    if data is None: data = DATA
    log_abs_dft = log10(abs(fft(x[:,1])))
    res_freq = sqrt(data['K']/data['M'])/(2*pi)
    print(f'Resonance frequency: {res_freq} Hz')
    n = len(t)
    ir = argmax(log_abs_dft[:n//2])
    # ar = max(log_abs_dft[:n//2])
    step = res_freq/(ir)
    ff = arange(0,res_freq*2,step)
    # mr = min(log_abs_dft[:len(ff)])
    log_amplitude = log_abs_dft[:len(ff)]
    return ff, log_amplitude


# if __name__ == '__main__':
    
#     t,x,f = msd_simulator()
#     fig,ax = pyplot.subplots(nrows=2,ncols=1,figsize=(10,6))
#     ax[0].plot(t,x[:,1])
#     ax[1].plot(t,f)
#     for axi in ax: 
#         axi.set_xlabel('t [s]')
#         if GRID: axi.grid()
#     ax[0].set_ylabel('x [m]')
#     ax[1].set_ylabel('F [N]')

#     freq, log_amplitude = fourier_transform(t,x)
#     fig,ax = pyplot.subplots(nrows=1,ncols=1,figsize=(10,6))
#     ax.plot(freq,log_amplitude)
#     ax.set_xlabel('F [Hz]')
#     if GRID: ax.grid()
#     ax.set_ylabel('A [DB]')

#     pyplot.show()
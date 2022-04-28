'''
This function calculates the kinetic energy of the original structure without control.
'''
from dtApp.dtData.soton_twin import Soton_twin_data

import numpy as np
import scipy.linalg as la
# import control.matlab as ctrmat
from plotly.subplots import make_subplots

from dtLib.third_party.python_control_v091.control.ctrlutil import mag2db

def keoriginal():
    fs = 1e2
    freq = np.arange(1, 1e2+1/fs, 1/fs)    # frequency vector
    ns = len(freq)

    # import geometric and physical data
    m = Soton_twin_data['structure']['mass']['value']   # mass of each storey
    b = Soton_twin_data['structure']['legWidth']['value']
    h = Soton_twin_data['structure']['legThickness']['value']
    l = Soton_twin_data['structure']['legLength']['value']
    E = Soton_twin_data['structure']['elasticityModulus']['value']
    J = b*pow(h,3)/12
    k = 4*12*E*J/pow(l,3)   # stiffness between each floor
    xi = Soton_twin_data['structure']['dampRatio']['value']     # damp ratio of first 2 modes

    # generate system matrices M, Ks
    Ms = np.diag([m,m,m])
    Ks = np.zeros((3,3))
    for ii in range(0,3):
        if ii==0:
            Ks[0][0]=k
        else:
            Ks[ii-1:ii+1,ii-1:ii+1] = Ks[ii-1:ii+1,ii-1:ii+1] + np.array([[k, -k], [-k, k]])

    # calculate eigenvalues and eigenvectors
    Wn, Xn = la.eig(Ks,Ms)
    Wn = Wn[::-1]       # vector of eigenvalues
    Xn = Xn[:,::-1]/np.sqrt(m)  # matrix of eigenvectors (mass normalised)

    # generate damping matrix C
    w1 = np.sqrt(Wn[0])
    w2 = np.sqrt(Wn[1])
    ray = (2*xi/(w1+w2))*np.array([[w1*w2], [1]]) # Rayleigh damping coefficients
    Cs = ray[0]*Ms + ray[1]*Ks

    # forcing matrices
    phip = np.zeros((1,3))
    phip[0][0] = 1

    T = np.zeros((ns),dtype=complex)
    for ii in range(0,ns):
        w = 2*np.pi*freq[ii]
        Z = 1j*w*Ms+Cs+Ks/(1j*w)
        dotX = la.inv(Z)@phip.transpose()
        T[ii] = (1/4)*dotX.conjugate().transpose()@Ms@dotX
        
    ITs = np.trapz(T.real, x=2*np.pi*freq)
    T_ = mag2db(abs(T))
    
    return {'freq': freq, 'ke': T_, 'IntKE': ITs}
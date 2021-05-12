'''
This function calculates the kinetic energy of the structure controlled by a Linear-Quadratic Gaussian regulator.
'''
from dtApp.dtData.soton_twin import Soton_twin_data
import numpy as np
import scipy.linalg as la
from control import *
import control.matlab as ctrmat
from plotly.subplots import make_subplots


def keLQG(nfs, mb, mp, kp, cp, Bl, Ze, q, r, Qn, Rn):
    fs = 1e2
    freq = np.arange(1, 1e2+1/fs, 1/fs)    # frequency vector
    ns = len(freq)
    ga = float(1)   # amplifier gain

    # import geometric and physical data
    m = Soton_twin_data['structure']['mass']['value']   # mass of each storey
    b = Soton_twin_data['structure']['legWidth']['value']
    ht = Soton_twin_data['structure']['legThickness']['value']
    l = Soton_twin_data['structure']['legLength']['value']
    E = Soton_twin_data['structure']['elasticityModulus']['value']
    J = b*pow(ht,3)/12
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
    # print('natural freq structure [Hz] \n', np.sqrt(Wn)/2/np.pi)

    # generate damping matrix C
    w1 = np.sqrt(Wn[0])
    w2 = np.sqrt(Wn[1])
    ray = (2*xi/(w1+w2))*np.array([[w1*w2], [1]]) # Rayleigh damping coefficients
    Cs = ray[0]*Ms + ray[1]*Ks

    # forcing matrices
    phip = np.zeros((1,3))
    phip[0][0] = 1
    phiptmd = np.block([phip, np.array([0])])
    phiptmdss = np.block([np.zeros((1,4)), phiptmd])

    phis = np.zeros((1,3))
    phis[0][nfs-1] = 1
    phistmd = np.block([phis, np.array([-1])])
    phistmdss = np.block([np.zeros((1,4)), phistmd])

    # system matrices - structure + TMD
    Msstar = Ms
    Msstar[nfs-1][nfs-1] += mb
    Mstmd = np.block([
        [Msstar, 0*phis.transpose()],
        [0*phis, np.array([mp])]
    ])

    Kstmd = np.block([
        [Ks+kp*phis.transpose()@phis, -kp*phis.transpose()],
        [-kp*phis, np.array([kp])]
    ])

    Cstmd = np.block([
        [Cs+cp*phis.transpose()@phis, -cp*phis.transpose()],
        [-cp*phis, np.array([cp])]
    ])

    # create state-space form
    A = np.block([
        [np.zeros((4,4)), np.eye(4)],
        [-la.inv(Mstmd)@Kstmd, -la.inv(Mstmd)@Cstmd]
        ])

    Bu = np.block([
        [np.zeros((4,4))],
        [la.inv(Mstmd)]
        ])@phistmd.transpose()

    Bd = -Bu

    Cvfc = np.zeros((1,8))
    Cvfc[0][2+nfs] = 1

    # create LQG regulator
    Clqr = np.eye(8)
    Q = q*Clqr.transpose()@Clqr
    Q[3][3] = 0
    Q[7][7] = 0
    R = [[r]]
    Klqg, Slqg, Elqg = lqr(A, Bu, Q, R)

    Clqg = Cvfc # the single output is the velocity co-located with the actuator


    gm = 1

    G = np.c_[np.zeros((8,1)), np.zeros((8,1)), np.zeros((8,1)), np.zeros((8,1)), ga*Bl*Bu, np.zeros((8,1)), np.zeros((8,1)), Bd]
    QN = Qn*np.eye(8)
    RN = [[Rn]]
    Lkal, Pkal, Eig = lqe(A, G, Clqg, QN, RN)

    T = np.zeros((ns),dtype=complex)
    L = np.zeros((ns),dtype=complex)
    P = np.zeros((ns),dtype=complex)
    for ii in range(0,ns):
        w = 2*np.pi*freq[ii]
        
        dotX = la.inv((1j*w*np.eye(8))-A+ga*Bl*Bu@Klqg@(la.inv((1j*w*np.eye(8))-A+Lkal@Clqg+ga*Bl*Bu@Klqg)@(Lkal*Clqg)))@Bd

        westLQG = (la.inv((1j*w*np.eye(8))-A+Lkal@Clqg+ga*Bl*Bu@Klqg)@(Lkal*Clqg))@dotX
        ULQG = -ga*Bl*Klqg@westLQG

        dotXs = np.delete(dotX, [0,1,2,3,7])
        T[ii] = (1/4)*dotXs.conjugate().transpose()@Msstar@dotXs

        L[ii] = (ga*Bl*Klqg@(la.inv((1j*w*np.eye(8))-A+Lkal@Clqg+ga*Bl*Bu@Klqg)@(Lkal*Clqg)))@(la.inv((1j*w*np.eye(8))-A)@Bu)

        P[ii] = ULQG.conjugate().transpose()@ULQG
        
    ITsvfc = np.trapz(T.real, x=2*np.pi*freq)
    IPvfc = np.trapz(P.real, x=2*np.pi*freq)
    T = ctrmat.mag2db(abs(T))
    return {'freq': freq, 'ke': T, 'ol':L, 'IntKE': ITsvfc, 'IntCE': IPvfc, 'Gm': gm}
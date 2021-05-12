'''
This function performs the control base continuation simulation of the structure with a stiffness nonlinearity. It also performs an amplitude sweep simulation and a frequency sweep simulation.
'''
import numpy as np
import scipy.linalg as la
import math
from scipy.integrate import odeint
import matplotlib.pyplot as plt

def Open_loop_3st(u,t,p,Minv,B,S,s13):
    Phi = p[0]
    omega = p[1]

    tmp1 = np.array([s13 * (u[3])**3, 0.0, 0.0])
    tmp2 = np.array([Phi * np.sin(omega*t), 0.0, 0.0])
    du13 = -Minv @ (B @ u[0:3] + S @ u[3:6] + tmp1 + tmp2)
    du46 = u[0:3]
    return np.concatenate((du13, du46), axis=None)

def freq_sweep_add(dudt,IC,Minv,B,S,s13,omega0,Phi0,Amplist,Amplist2,Amplist3,fsw_per):
    IC_act = IC

    tend = fsw_per*2*math.pi/omega0
    tlist = np.linspace(0, tend, 501)

    sol = odeint(dudt, IC_act, tlist, args=(np.array([Phi0, omega0]), Minv, B, S, s13))

    Amp = (max(sol[400:-1,3]) - min(sol[400:-1,3]))/2.0
    Amp2 = (max(sol[400:-1,4]) - min(sol[400:-1,4]))/2.0
    Amp3 = (max(sol[400:-1,5]) - min(sol[400:-1,5]))/2.0
    Amplist = np.append(Amplist, Amp)
    Amplist2 = np.append(Amplist2, Amp2)
    Amplist3 = np.append(Amplist3, Amp3)

    IC_act = sol[-1,:]


    return Amplist, Amplist2, Amplist3, IC_act

def harm_calc(t, y, trapz, k, omega):
    coefflist = np.zeros((k+1)*2)
    for ii in range(k+1):
        coefflist[ii] = omega/math.pi*trapz(t,y*np.cos(ii*omega*t))
    for ii in range(k+1):
        coefflist[ii+k+1] = omega/math.pi*trapz(t,y*np.sin(ii*omega*t))
    return coefflist

def trapz(x, y):
    Itg = 0.0
    for ii in range(len(x)-1):
        Itg += 0.5 * (y[ii]+y[ii+1]) * (x[ii+1]-x[ii])
    return Itg

def amp_sweep_add(dudt,IC,Minv,B,S,s13,Phi0,omega0,Amplist,Amplist2,Amplist3,k,asw_per):
    IC_act = IC

    tend = asw_per*2*math.pi/omega0
    tlist = np.linspace(0, tend, asw_per*250+1)

    sol = odeint(dudt, IC_act, tlist, args=(np.array([Phi0, omega0]), Minv, B, S, s13))

    tsel = tlist[-251:-1]
    solsel = sol[-251:-1,3]
    solsel2 = sol[-251:-1,4]
    solsel3 = sol[-251:-1,5]

    coeffs = harm_calc(tsel, solsel, trapz, k, omega0)
    coeffs2 = harm_calc(tsel, solsel2, trapz, k, omega0)
    coeffs3 = harm_calc(tsel, solsel3, trapz, k, omega0)

    Amp = (coeffs[1]**2+coeffs[k+2]**2)**0.5
    Amp2 = (coeffs2[1]**2+coeffs2[k+2]**2)**0.5
    Amp3 = (coeffs3[1]**2+coeffs3[k+2]**2)**0.5

    Amplist = np.append(Amplist, Amp)
    Amplist2 = np.append(Amplist2, Amp2)
    Amplist3 = np.append(Amplist3, Amp3)

    IC_act = sol[-1,:]


    return Amplist, Amplist2, Amplist3, IC_act

def CBC_3st(u,t,p,Minv,B,S,s13,kp,kd,target_coeff,dtarget_coeff,k):
    omega = p[0]
    Astar = p[1]
    Bstar = p[2]

    sins = np.zeros(k+1)
    coss = np.zeros(k+1)

    for ii in range(k+1):

        sins[ii] = np.sin(ii*t*omega)
        coss[ii] = np.cos(ii*t*omega)

    hmcs = np.concatenate((coss, sins), axis=0, out=None)
    target = sum(target_coeff*hmcs) - target_coeff[0]*0.5
    dtarget = sum(dtarget_coeff*hmcs)

    tmp1 = np.array([s13 * (u[3])**3, 0.0, 0.0])
    tmp2 = np.array([Astar * np.cos(omega*t) + Bstar * np.sin(omega*t), 0.0, 0.0])
    ctr = np.array([kp * (target - u[3]) + kd * (dtarget - u[0]), 0.0, 0.0])
    du13 = -Minv @ (B @ u[0:3] + S @ u[3:6] + tmp1 + tmp2 + ctr)
    du46 = u[0:3]
    return np.concatenate((du13, du46), axis=None)

def continuation(dudt,trapz,omega_sel,Minv,B,S,s13,kp,kd,target_coeff,dtarget_coeff,k,branch,IC_act,Astar1,Bstar1,Target_c_list,Target_s_list,maxit,etol,cbc_per):

    tend = cbc_per*(2*math.pi/omega_sel)
    tlist = np.linspace(0.0, tend, cbc_per*500+1)
    coeffs = target_coeff

    for ii in range(len(Target_c_list)):
        target_coeff[1] = Target_c_list[ii]
        target_coeff[k+2] = Target_s_list[ii]

      

        dtarget_coeff[0:k+1] = omega_sel * np.array(range(k+1)) * target_coeff[k+1:]
        dtarget_coeff[k+1:] = -omega_sel * np.array(range(k+1)) * target_coeff[0:k+1]

        sol = odeint(dudt, IC_act, tlist, args=(np.array([omega_sel, Astar1, Bstar1]), Minv, B, S, s13, kp, kd, target_coeff, dtarget_coeff, k))
        IC_act = sol[-1,:]
        tsel = tlist[-501:-1]
        solsel = sol[-501:-1,3]
        solsel2 = sol[-501:-1,4]
        solsel3 = sol[-501:-1,5]

        coeff_pred = coeffs

        coeffs = harm_calc(tsel, solsel, trapz, k, omega_sel)
        coeffs2 = harm_calc(tsel, solsel2, trapz, k, omega_sel)
        coeffs3 = harm_calc(tsel, solsel3, trapz, k, omega_sel)
        err = la.norm(coeff_pred[2:k+2]-coeffs[2:k+2]) + la.norm(coeff_pred[k+3:]-coeffs[k+3:]) + la.norm(coeff_pred[0]-coeffs[0])

        Astar1 = Astar1 + kp * (target_coeff[1]-coeffs[1]) + kd * omega_sel * (target_coeff[k+2]-coeffs[k+2])
        Bstar1 = Bstar1 + kp * (target_coeff[k+2]-coeffs[k+2]) - kd * omega_sel * (target_coeff[1]-coeffs[1])

        target_coeff[0] = coeffs[0]
        target_coeff[2:k+2] = coeffs[2:k+2]
        target_coeff[k+3:] = coeffs[k+3:]
        dtarget_coeff[0:k+1] = omega_sel * np.array(range(k+1)) * target_coeff[k+1:]
        dtarget_coeff[k+1:] = -omega_sel * np.array(range(k+1)) * target_coeff[0:k+1]


        itnum = 1

        while err > etol and itnum <= maxit:

            dtarget_coeff[0:k+1] = omega_sel * np.array(range(k+1)) * target_coeff[k+1:]
            dtarget_coeff[k+1:] = -omega_sel * np.array(range(k+1)) * target_coeff[0:k+1]

            sol = odeint(dudt, IC_act, tlist, args=(np.array([omega_sel, Astar1, Bstar1]), Minv, B, S, s13, kp, kd, target_coeff, dtarget_coeff, k))
            IC_act = sol[-1,:]
            tsel = tlist[-501:-1]
            solsel = sol[-501:-1,3]
            solsel2 = sol[-501:-1,4]
            solsel3 = sol[-501:-1,5]

            coeff_pred = coeffs

            coeffs = harm_calc(tsel, solsel, trapz, k, omega_sel)
            coeffs2 = harm_calc(tsel, solsel2, trapz, k, omega_sel)
            coeffs3 = harm_calc(tsel, solsel3, trapz, k, omega_sel)
            err = la.norm(coeff_pred[2:k+2]-coeffs[2:k+2]) + la.norm(coeff_pred[k+3:]-coeffs[k+3:]) + la.norm(coeff_pred[0]-coeffs[0])
            

            Astar1 = Astar1 + kp * (target_coeff[1]-coeffs[1]) + kd * omega_sel * (target_coeff[k+2]-coeffs[k+2])
            Bstar1 = Bstar1 + kp * (target_coeff[k+2]-coeffs[k+2]) - kd * omega_sel * (target_coeff[1]-coeffs[1])

            target_coeff[0] = coeffs[0]
            target_coeff[2:k+2] = coeffs[2:k+2]
            target_coeff[k+3:] = coeffs[k+3:]
            dtarget_coeff[0:k+1] = omega_sel * np.array(range(k+1)) * target_coeff[k+1:]
            dtarget_coeff[k+1:] = -omega_sel * np.array(range(k+1)) * target_coeff[0:k+1]

            

            itnum += 1

        newbp = [(Astar1**2+Bstar1**2)**0.5, (coeffs[1]**2+coeffs[k+2]**2)**0.5, (coeffs2[1]**2+coeffs2[k+2]**2)**0.5, (coeffs3[1]**2+coeffs3[k+2]**2)**0.5]
        branch = np.append(branch, [newbp], axis=0)

    return branch, IC_act, Astar1, Bstar1, coeffs

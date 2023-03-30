'''
Route script used for running Control-based continuation.
'''
# import required packages
import numpy as np
import scipy.linalg as la
import math
from flask import render_template, request, redirect, Response, url_for, flash, send_file
import json, os
from scipy.integrate import odeint
from pathlib import Path

from digitaltwin import date
import digitaltwin.dtLib.nonlinearcbc.nonlinearcbc2 as cbc2

def bristolcbc():
    # define input data
    path_like = os.path.join("digitaltwin","dtData","CBC")
    pars_file = Path(os.path.join(path_like,"bris_pars.npy"))
    if pars_file.is_file():
        # file exists
        pars = np.load(pars_file)

        m1, m2, m3 = pars[0], pars[1], pars[2]
        b1, b2, b3 = pars[3], pars[4], pars[5]
        s1, s2, s3 = pars[6], pars[7], pars[8]
        s13 = pars[9]
    else:

        m1, m2, m3 = 0.2, 0.2, 0.2 #masses
        s1, s2, s3, s13 = 200.0, 200.0, 200.0, 200.0 #stiffnesses
        b1, b2, b3 = 0.1, 0.1, 0.1 #viscous damping

    sweep_file = Path(os.path.join(path_like,"sweep_pars.npy"))
    if sweep_file.is_file():
        # file exists
        sweep_pars = np.load(sweep_file)
        
    else:

        sweep_pars = np.array([1.0, 50.0, 1.0, 80.0, 0.945])


    #Mass, damping and stiffness matrices
    MM = np.array([[m1, 0.0, 0.0], [0.0, m2, 0.0], [0.0, 0.0, m3]])
    BB = np.array([[b1+b2, -b2, 0.0], [-b2, b2+b3, -b3], [0.0, -b3, b3]])
    SS = np.array([[s1+s2, -s2, 0.0], [-s2, s2+s3, -s3], [0.0, -s3, s3]])
    Minv = la.inv(MM)

    IC = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    Minfreq = sweep_pars[0]
    Maxfreq = sweep_pars[1]

    Freq_list_def = np.linspace(Minfreq, Maxfreq, 200)

    Min_exc_amp = sweep_pars[2]
    Max_exc_amp = sweep_pars[3]

    Exc_amp_list_def = np.linspace(Min_exc_amp, Max_exc_amp, 40)

    Freq_list_up = np.empty(shape=(0))
    Freq_list_down = np.empty(shape=(0))
    Amplist_up = np.empty(shape=(0))
    Amplist_down = np.empty(shape=(0))
    Amplist_up2 = np.empty(shape=(0))
    Amplist_down2 = np.empty(shape=(0))
    Amplist_up3 = np.empty(shape=(0))
    Amplist_down3 = np.empty(shape=(0))

    Exc_amp_list_incr = np.empty(shape=(0))
    Exc_amp_list_decr = np.empty(shape=(0))
    Amplist_incr = np.empty(shape=(0))
    Amplist_decr = np.empty(shape=(0))
    Amplist_incr2 = np.empty(shape=(0))
    Amplist_decr2 = np.empty(shape=(0))
    Amplist_incr3 = np.empty(shape=(0))
    Amplist_decr3 = np.empty(shape=(0))

    branch_cont = np.empty(shape=(0, 4))
    IC = np.zeros(6)
    status = np.array([1.0])

    np.save(os.path.join(path_like,"Freq_list_def.npy"), Freq_list_def)
    np.save(os.path.join(path_like,"Freq_list_up.npy"), Freq_list_up)
    np.save(os.path.join(path_like,"Freq_list_down.npy"), Freq_list_down)
    np.save(os.path.join(path_like,"Amplist_up.npy"), Amplist_up)
    np.save(os.path.join(path_like,"Amplist_down.npy"), Amplist_down)
    np.save(os.path.join(path_like,"Amplist_up2.npy"), Amplist_up2)
    np.save(os.path.join(path_like,"Amplist_down2.npy"), Amplist_down2)
    np.save(os.path.join(path_like,"Amplist_up3.npy"), Amplist_up3)
    np.save(os.path.join(path_like,"Amplist_down3.npy"), Amplist_down3)

    np.save(os.path.join(path_like,"Exc_amp_list_def.npy"), Exc_amp_list_def)
    np.save(os.path.join(path_like,"Exc_amp_list_incr.npy"), Exc_amp_list_incr)
    np.save(os.path.join(path_like,"Exc_amp_list_decr.npy"), Exc_amp_list_decr)
    np.save(os.path.join(path_like,"Amplist_incr.npy"), Amplist_incr)
    np.save(os.path.join(path_like,"Amplist_decr.npy"), Amplist_decr)
    np.save(os.path.join(path_like,"Amplist_incr2.npy"), Amplist_incr2)
    np.save(os.path.join(path_like,"Amplist_decr2.npy"), Amplist_decr2)
    np.save(os.path.join(path_like,"Amplist_incr3.npy"), Amplist_incr3)
    np.save(os.path.join(path_like,"Amplist_decr3.npy"), Amplist_decr3)

    np.save(os.path.join(path_like,"branch_cont.npy"), branch_cont)
    np.save(os.path.join(path_like,"IC.npy"), IC)
    np.save(os.path.join(path_like,"mode.npy"), status)

    np.save(os.path.join(path_like,"Exc_amp_list_incr_cbc.npy"), Exc_amp_list_incr)
    np.save(os.path.join(path_like,"Exc_amp_list_decr_cbc.npy"), Exc_amp_list_decr)
    np.save(os.path.join(path_like,"Amplist_incr_cbc.npy"), Amplist_incr)
    np.save(os.path.join(path_like,"Amplist_decr_cbc.npy"), Amplist_decr)

    graph1 = cbc2.cbc_dataplot(Freq_list_up, Freq_list_down, Amplist_up, Amplist_down, Exc_amp_list_incr, Exc_amp_list_decr, Amplist_incr, Amplist_decr, branch_cont, Exc_amp_list_incr, Exc_amp_list_decr, Amplist_incr, Amplist_decr)

    return render_template("nonlinearcbc.html", plot=graph1,date=date)

def par_submit():
    path_like = os.path.join("digitaltwin","dtData","CBC")
    if request.method=='POST':
        req = request.form
        # print(req)

        m1 = float(req.get("m1"))
        m2 = float(req.get("m2"))
        m3 = float(req.get("m3"))
        s1 = float(req.get("s1"))
        s2 = float(req.get("s2"))
        s3 = float(req.get("s3"))
        b1 = float(req.get("b1"))
        b2 = float(req.get("b2"))
        b3 = float(req.get("b3"))
        s13 = float(req.get("s13"))
        F0 = float(req.get("F0"))
        om0 = float(req.get("om0"))
        kp = float(req.get("kp"))
        kd = float(req.get("kd"))

        om_min = float(req.get("om_min"))
        om_max = float(req.get("om_max"))
        F_min = float(req.get("F_min"))
        F_max = float(req.get("F_max"))
        A_max = float(req.get("A_max"))

        fsw_per = int(req.get("fsw_per"))
        asw_per = int(req.get("asw_per"))
        cbc_per = int(req.get("cbc_per"))
        cbc_maxiter = int(req.get("cbc_maxiter"))
        cbc_etol = float(req.get("cbc_etol"))
        
        pars = np.array([m1, m2, m3, b1, b2, b3, s1, s2, s3, s13, F0, om0, kp, kd])
        np.save(os.path.join(path_like,"pars.npy"), pars)

        sweep_pars = np.array([om_min, om_max, F_min, F_max, A_max])
        np.save(os.path.join(path_like,"sweep_pars.npy"), sweep_pars)
        
        np.save(os.path.join(path_like,"fsw_per.npy"), fsw_per)
        np.save(os.path.join(path_like,"asw_per.npy"), asw_per)
        np.save(os.path.join(path_like,"cbc_per.npy"), cbc_per)
        np.save(os.path.join(path_like,"cbc_maxiter.npy"), cbc_maxiter)
        np.save(os.path.join(path_like,"cbc_etol.npy"), cbc_etol)

        Freq_list_def = np.load(os.path.join(path_like,"Freq_list_def.npy"))
        Freq_list_up = np.load(os.path.join(path_like,"Freq_list_up.npy"))
        Freq_list_down = np.load(os.path.join(path_like,"Freq_list_down.npy"))
        Amplist_up = np.load(os.path.join(path_like,"Amplist_up.npy"))
        Amplist_down = np.load(os.path.join(path_like,"Amplist_down.npy"))
        Exc_amp_list_def = np.load(os.path.join(path_like,"Exc_amp_list_def.npy"))
        Exc_amp_list_incr = np.load(os.path.join(path_like,"Exc_amp_list_incr.npy"))
        Exc_amp_list_decr = np.load(os.path.join(path_like,"Exc_amp_list_decr.npy"))
        Amplist_incr = np.load(os.path.join(path_like,"Amplist_incr.npy"))
        Amplist_decr = np.load(os.path.join(path_like,"Amplist_decr.npy"))
        branch_cont = np.load(os.path.join(path_like,"branch_cont.npy"))
        IC = np.load(os.path.join(path_like,"IC.npy"))

        Exc_amp_list_incr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_incr_cbc.npy"))
        Exc_amp_list_decr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_decr_cbc.npy"))
        Amplist_incr_cbc = np.load(os.path.join(path_like,"Amplist_incr_cbc.npy"))
        Amplist_decr_cbc = np.load(os.path.join(path_like,"Amplist_decr_cbc.npy"))

        Minfreq = sweep_pars[0]
        Maxfreq = sweep_pars[1]

        Freq_list_def = np.linspace(Minfreq, Maxfreq, 200)

        Min_exc_amp = sweep_pars[2]
        Max_exc_amp = sweep_pars[3]

        Exc_amp_list_def = np.linspace(Min_exc_amp, Max_exc_amp, 40)

        np.save(os.path.join(path_like,"Freq_list_def.npy"), Freq_list_def)
        np.save(os.path.join(path_like,"Exc_amp_list_def.npy"), Exc_amp_list_def)

        graph1 = cbc2.cbc_dataplot(Freq_list_up, Freq_list_down, Amplist_up, Amplist_down, Exc_amp_list_incr, Exc_amp_list_decr, Amplist_incr, Amplist_decr, branch_cont, Exc_amp_list_incr_cbc, Exc_amp_list_decr_cbc, Amplist_incr_cbc, Amplist_decr_cbc)

    return render_template("nonlinearcbc2.html", plot=graph1, m1=m1, m2=m2, m3=m3, s1=s1, s2=s2, s3=s3, b1=b1, b2=b2, b3=b3, s13=s13, F0=F0, om0=om0, kp=kp, kd=kd, fsw_per=fsw_per, asw_per=asw_per, cbc_per=cbc_per, cbc_maxiter=cbc_maxiter, cbc_etol=cbc_etol, om_min=om_min, om_max=om_max, F_min=F_min, F_max=F_max, A_max=A_max,date=date)


def downloadFile ():
    path_like = os.path.join("digitaltwin","dtData","CBC")
    path = os.path.join(path_like,"data_download.txt")
    path_d = os.path.join("dtData","CBC","data_download.txt")

    Freq_list_def = np.load(os.path.join(path_like,"Freq_list_def.npy"))
    Freq_list_up = np.load(os.path.join(path_like,"Freq_list_up.npy"))
    Freq_list_down = np.load(os.path.join(path_like,"Freq_list_down.npy"))
    Amplist_up = np.load(os.path.join(path_like,"Amplist_up.npy"))
    Amplist_down = np.load(os.path.join(path_like,"Amplist_down.npy"))
    Amplist_up2 = np.load(os.path.join(path_like,"Amplist_up2.npy"))
    Amplist_down2 = np.load(os.path.join(path_like,"Amplist_down2.npy"))
    Amplist_up3 = np.load(os.path.join(path_like,"Amplist_up3.npy"))
    Amplist_down3 = np.load(os.path.join(path_like,"Amplist_down3.npy"))
    Exc_amp_list_def = np.load(os.path.join(path_like,"Exc_amp_list_def.npy"))
    Exc_amp_list_incr = np.load(os.path.join(path_like,"Exc_amp_list_incr.npy"))
    Exc_amp_list_decr = np.load(os.path.join(path_like,"Exc_amp_list_decr.npy"))
    Amplist_incr = np.load(os.path.join(path_like,"Amplist_incr.npy"))
    Amplist_decr = np.load(os.path.join(path_like,"Amplist_decr.npy"))
    Amplist_incr2 = np.load(os.path.join(path_like,"Amplist_incr2.npy"))
    Amplist_decr2 = np.load(os.path.join(path_like,"Amplist_decr2.npy"))
    Amplist_incr3 = np.load(os.path.join(path_like,"Amplist_incr3.npy"))
    Amplist_decr3 = np.load(os.path.join(path_like,"Amplist_decr3.npy"))
    branch_cont = np.load(os.path.join(path_like,"branch_cont.npy"))

    if (Path(path)).is_file():
        pass    
    else:
        f = open(path, "x")
        f.close()
    
    f = open(path, "w")
    f.write("//RESULTS//")
    f.write("\n")
    f.write("\n")
    f.write("//#Frequency sweep//")
    f.write("\n")
    f.write("\n")
    f.write("/Increasing frequency/*")
    f.write("\n")
    f.write("\n")
    f.write("f [Hz] A_x1 [m] A_x2 [m] A_x3 [m]")

    len = Freq_list_up.size
    for ii in range(0, len):
        f.write("\n")
        f.write(str(Freq_list_up[ii]))
        f.write(" ")
        f.write(str(Amplist_up[ii]))
        f.write(" ")
        f.write(str(Amplist_up2[ii]))
        f.write(" ")
        f.write(str(Amplist_up3[ii]))

    f.write("\n")
    f.write("\n")

    f.write("/Decreasing frequency/")
    f.write("\n")
    f.write("\n")
    f.write("f [Hz] A_x1 [m] A_x2 [m] A_x3 [m]")

    len = Freq_list_down.size
    for ii in range(0, len):
        f.write("\n")
        f.write(str(Freq_list_down[ii]))
        f.write(" ")
        f.write(str(Amplist_down[ii]))
        f.write(" ")
        f.write(str(Amplist_down2[ii]))
        f.write(" ")
        f.write(str(Amplist_down3[ii]))

    f.write("\n")
    f.write("\n")

    f.write("//Amplitude sweep//")
    f.write("\n")
    f.write("\n")
    f.write("/Increasing amplitude/")
    f.write("\n")
    f.write("\n")
    f.write("Phi [N] A_x1 [m] A_x2 [m] A_x3 [m]")

    a_len = Exc_amp_list_incr.size
    for ii in range(0, a_len):
        f.write("\n")
        f.write(str(Exc_amp_list_incr[ii]))
        f.write(" ")
        f.write(str(Amplist_incr[ii]))
        f.write(" ")
        f.write(str(Amplist_incr2[ii]))
        f.write(" ")
        f.write(str(Amplist_incr3[ii]))
    
    f.write("\n")
    f.write("\n")

    f.write("/Decreasing amplitude/")
    f.write("\n")
    f.write("\n")
    f.write("Phi [N] A_x1 [m] A_x2 [m] A_x3 [m]")

    a_len = Exc_amp_list_decr.size
    for ii in range(0, a_len):
        f.write("\n")
        f.write(str(Exc_amp_list_decr[ii]))
        f.write(" ")
        f.write(str(Amplist_decr[ii]))
        f.write(" ")
        f.write(str(Amplist_decr2[ii]))
        f.write(" ")
        f.write(str(Amplist_decr3[ii]))

    f.write("\n")
    f.write("\n")

    f.write("//Control-based continuation in amplitude//")
    f.write("\n")
    f.write("\n")
    f.write("Phi [N] A_x1 [m] A_x2 [m] A_x3 [m]")

    cbc_x = branch_cont[:,0]
    cbc_y = branch_cont[:,1]
    cbc_A1 = branch_cont[:,2]
    cbc_A2 = branch_cont[:,3]

    cbc_len = cbc_x.size
    for ii in range(0, cbc_len):
        f.write("\n")
        f.write(str(cbc_x[ii]))
        f.write(" ")
        f.write(str(cbc_y[ii]))
        f.write(" ")
        f.write(str(cbc_A1[ii]))
        f.write(" ")
        f.write(str(cbc_A2[ii]))



    f.close()


    return send_file(path_d, as_attachment=True)

def bristolcbc_update_fws():
    # define input data
    path_like = os.path.join("digitaltwin","dtData","CBC")
    pars_file = Path(os.path.join(path_like,"pars.npy"))
    if pars_file.is_file():
        # file exists
        pars = np.load(os.path.join(path_like,"pars.npy"))

        m1, m2, m3 = pars[0], pars[1], pars[2]
        b1, b2, b3 = pars[3], pars[4], pars[5]
        s1, s2, s3 = pars[6], pars[7], pars[8]
        s13 = pars[9]
        Phi0 = pars[10]

    else:

        m1, m2, m3 = 0.2, 0.2, 0.2 #masses
        s1, s2, s3, s13 = 200.0, 200.0, 200.0, 200.0 #stiffnesses
        b1, b2, b3 = 0.1, 0.1, 0.1 #viscous damping
        Phi0 = 10.0

    #Mass, damping and stiffness matrices
    MM = np.array([[m1, 0.0, 0.0], [0.0, m2, 0.0], [0.0, 0.0, m3]])
    BB = np.array([[b1+b2, -b2, 0.0], [-b2, b2+b3, -b3], [0.0, -b3, b3]])
    SS = np.array([[s1+s2, -s2, 0.0], [-s2, s2+s3, -s3], [0.0, -s3, s3]])
    Minv = la.inv(MM)

    Freq_list_def = np.load(os.path.join(path_like,"Freq_list_def.npy"))
    Freq_list_up = np.load(os.path.join(path_like,"Freq_list_up.npy"))
    Freq_list_down = np.load(os.path.join(path_like,"Freq_list_down.npy"))
    Amplist_up = np.load(os.path.join(path_like,"Amplist_up.npy"))
    Amplist_down = np.load(os.path.join(path_like,"Amplist_down.npy"))
    Amplist_up2 = np.load(os.path.join(path_like,"Amplist_up2.npy"))
    Amplist_down2 = np.load(os.path.join(path_like,"Amplist_down2.npy"))
    Amplist_up3 = np.load(os.path.join(path_like,"Amplist_up3.npy"))
    Amplist_down3 = np.load(os.path.join(path_like,"Amplist_down3.npy"))
    Exc_amp_list_def = np.load(os.path.join(path_like,"Exc_amp_list_def.npy"))
    Exc_amp_list_incr = np.load(os.path.join(path_like,"Exc_amp_list_incr.npy"))
    Exc_amp_list_decr = np.load(os.path.join(path_like,"Exc_amp_list_decr.npy"))
    Amplist_incr = np.load(os.path.join(path_like,"Amplist_incr.npy"))
    Amplist_decr = np.load(os.path.join(path_like,"Amplist_decr.npy"))
    Amplist_incr2 = np.load(os.path.join(path_like,"Amplist_incr2.npy"))
    Amplist_decr2 = np.load(os.path.join(path_like,"Amplist_decr2.npy"))
    Amplist_incr3 = np.load(os.path.join(path_like,"Amplist_incr3.npy"))
    Amplist_decr3 = np.load(os.path.join(path_like,"Amplist_decr3.npy"))
    branch_cont = np.load(os.path.join(path_like,"branch_cont.npy"))
    IC = np.load(os.path.join(path_like,"IC.npy"))

    Exc_amp_list_incr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_incr_cbc.npy"))
    Exc_amp_list_decr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_decr_cbc.npy"))
    Amplist_incr_cbc = np.load(os.path.join(path_like,"Amplist_incr_cbc.npy"))
    Amplist_decr_cbc = np.load(os.path.join(path_like,"Amplist_decr_cbc.npy"))

    fsw_per = np.load(os.path.join(path_like,"fsw_per.npy"))

    mode = request.args.get('value', 0, type=int)

    # Initialise plotted arrays
    if mode < 400:

        status = np.array([1.0])
        np.save(os.path.join(path_like,"mode.npy"), status)
        # Forcing
        #Phi0 = 10.0

        if len(Amplist_up) < len(Freq_list_def):
            itn = len(Amplist_up) + 1
            Amplist_up, Amplist_up2, Amplist_up3, IC = cbc2.freq_sweep_add(cbc2.Open_loop_3st,IC,Minv,BB,SS,s13,Freq_list_def[itn-1],Phi0,Amplist_up,Amplist_up2,Amplist_up3,fsw_per)
            Freq_list_up = np.append(Freq_list_up, Freq_list_def[itn-1])


        elif len(Amplist_down) < len(Freq_list_def):
            itn = len(Amplist_down) + 1
            Amplist_down, Amplist_down2, Amplist_down3, IC = cbc2.freq_sweep_add(cbc2.Open_loop_3st,IC,Minv,BB,SS,s13,Freq_list_def[-itn],Phi0,Amplist_down,Amplist_down2,Amplist_down3,fsw_per)
            Freq_list_down = np.append(Freq_list_down, Freq_list_def[-itn])
        else:
            status = np.array([0.0])
            np.save(os.path.join(path_like,"bris_mode.npy"), status)

        np.save(os.path.join(path_like,"Freq_list_up.npy"), Freq_list_up)
        np.save(os.path.join(path_like,"Freq_list_down.npy"), Freq_list_down)
        np.save(os.path.join(path_like,"Amplist_up.npy"), Amplist_up)
        np.save(os.path.join(path_like,"Amplist_down.npy"), Amplist_down)
        np.save(os.path.join(path_like,"Amplist_up2.npy"), Amplist_up2)
        np.save(os.path.join(path_like,"Amplist_down2.npy"), Amplist_down2)
        np.save(os.path.join(path_like,"Amplist_up3.npy"), Amplist_up3)
        np.save(os.path.join(path_like,"Amplist_down3.npy"), Amplist_down3)
        np.save(os.path.join(path_like,"IC.npy"), IC)

    graph1 = cbc2.cbc_dataplot(Freq_list_up, Freq_list_down, Amplist_up, Amplist_down, Exc_amp_list_incr, Exc_amp_list_decr, Amplist_incr, Amplist_decr, branch_cont, Exc_amp_list_incr_cbc, Exc_amp_list_decr_cbc, Amplist_incr_cbc, Amplist_decr_cbc)

    return graph1

def bristolcbc_update_asw():
    # define input data
    path_like = os.path.join("digitaltwin","dtData","CBC")
    pars_file = Path(os.path.join(path_like,"bris_pars.npy"))
    if pars_file.is_file():
        # file exists
        pars = np.load(os.path.join(path_like,"bris_pars.npy"))

        m1, m2, m3 = pars[0], pars[1], pars[2]
        b1, b2, b3 = pars[3], pars[4], pars[5]
        s1, s2, s3 = pars[6], pars[7], pars[8]
        s13 = pars[9]

        omega_sel = pars[11]

    else:

        m1, m2, m3 = 0.2, 0.2, 0.2 #masses
        s1, s2, s3, s13 = 200.0, 200.0, 200.0, 200.0 #stiffnesses
        b1, b2, b3 = 0.1, 0.1, 0.1 #viscous damping

        omega_sel = 16.0

    #Mass, damping and stiffness matrices
    MM = np.array([[m1, 0.0, 0.0], [0.0, m2, 0.0], [0.0, 0.0, m3]])
    BB = np.array([[b1+b2, -b2, 0.0], [-b2, b2+b3, -b3], [0.0, -b3, b3]])
    SS = np.array([[s1+s2, -s2, 0.0], [-s2, s2+s3, -s3], [0.0, -s3, s3]])
    Minv = la.inv(MM)

    Freq_list_def = np.load(os.path.join(path_like,"Freq_list_def.npy"))
    Freq_list_up = np.load(os.path.join(path_like,"Freq_list_up.npy"))
    Freq_list_down = np.load(os.path.join(path_like,"Freq_list_down.npy"))
    Amplist_up = np.load(os.path.join(path_like,"Amplist_up.npy"))
    Amplist_down = np.load(os.path.join(path_like,"Amplist_down.npy"))
    Amplist_up2 = np.load(os.path.join(path_like,"Amplist_up2.npy"))
    Amplist_down2 = np.load(os.path.join(path_like,"Amplist_down2.npy"))
    Amplist_up3 = np.load(os.path.join(path_like,"Amplist_up3.npy"))
    Amplist_down3 = np.load(os.path.join(path_like,"Amplist_down3.npy"))
    Exc_amp_list_def = np.load(os.path.join(path_like,"Exc_amp_list_def.npy"))
    Exc_amp_list_incr = np.load(os.path.join(path_like,"Exc_amp_list_incr.npy"))
    Exc_amp_list_decr = np.load(os.path.join(path_like,"Exc_amp_list_decr.npy"))
    Amplist_incr = np.load(os.path.join(path_like,"Amplist_incr.npy"))
    Amplist_decr = np.load(os.path.join(path_like,"Amplist_decr.npy"))
    Amplist_incr2 = np.load(os.path.join(path_like,"Amplist_incr2.npy"))
    Amplist_decr2 = np.load(os.path.join(path_like,"Amplist_decr2.npy"))
    Amplist_incr3 = np.load(os.path.join(path_like,"Amplist_incr3.npy"))
    Amplist_decr3 = np.load(os.path.join(path_like,"Amplist_decr3.npy"))
    branch_cont = np.load(os.path.join(path_like,"branch_cont.npy"))
    IC = np.load(os.path.join(path_like,"IC.npy"))

    Exc_amp_list_incr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_incr_cbc.npy"))
    Exc_amp_list_decr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_decr_cbc.npy"))
    Amplist_incr_cbc = np.load(os.path.join(path_like,"Amplist_incr_cbc.npy"))
    Amplist_decr_cbc = np.load(os.path.join(path_like,"Amplist_decr_cbc.npy"))

    asw_per = np.load(os.path.join(path_like,"asw_per.npy"))

    mode = request.args.get('value', 0, type=int)

    k = 10

    # Initialise plotted arrays
    if mode < 80:

        status = np.array([1.0])
        np.save(os.path.join(path_like,"mode.npy"), status)
        # Forcing
        #omega_sel = 16.0

        if len(Amplist_incr) < len(Exc_amp_list_def):
            itn = len(Amplist_incr) + 1
            Amplist_incr, Amplist_incr2, Amplist_incr3, IC = cbc2.amp_sweep_add(cbc2.Open_loop_3st,IC,Minv,BB,SS,s13,Exc_amp_list_def[itn-1],omega_sel,Amplist_incr,Amplist_incr2,Amplist_incr3,k,asw_per)
            Exc_amp_list_incr = np.append(Exc_amp_list_incr, Exc_amp_list_def[itn-1])


        elif len(Amplist_decr) < len(Exc_amp_list_def):
            itn = len(Amplist_decr) + 1
            Amplist_decr,  Amplist_decr2,  Amplist_decr3, IC = cbc2.amp_sweep_add(cbc2.Open_loop_3st,IC,Minv,BB,SS,s13,Exc_amp_list_def[-itn],omega_sel,Amplist_decr,Amplist_decr2,Amplist_decr3,k,asw_per)
            Exc_amp_list_decr = np.append(Exc_amp_list_decr, Exc_amp_list_def[-itn])
        else:
            status = np.array([0.0])
            np.save(os.path.join(path_like,"bris_mode.npy"), status)

        np.save(os.path.join(path_like,"Exc_amp_list_incr.npy"), Exc_amp_list_incr)
        np.save(os.path.join(path_like,"Exc_amp_list_decr.npy"), Exc_amp_list_decr)
        np.save(os.path.join(path_like,"Amplist_incr.npy"), Amplist_incr)
        np.save(os.path.join(path_like,"Amplist_decr.npy"), Amplist_decr)
        np.save(os.path.join(path_like,"Amplist_incr2.npy"), Amplist_incr2)
        np.save(os.path.join(path_like,"Amplist_decr2.npy"), Amplist_decr2)
        np.save(os.path.join(path_like,"Amplist_incr3.npy"), Amplist_incr3)
        np.save(os.path.join(path_like,"Amplist_decr3.npy"), Amplist_decr3)
        np.save(os.path.join(path_like,"IC.npy"), IC)


    graph1 = cbc2.cbc_dataplot(Freq_list_up, Freq_list_down, Amplist_up, Amplist_down, Exc_amp_list_incr, Exc_amp_list_decr, Amplist_incr, Amplist_decr, branch_cont, Exc_amp_list_incr_cbc, Exc_amp_list_decr_cbc, Amplist_incr_cbc, Amplist_decr_cbc)

    return graph1

def bristolcbc_update_cbc():
    path_like = os.path.join("digitaltwin","dtData","CBC")
    pars_file = Path(os.path.join(path_like,"pars.npy"))
    if pars_file.is_file():
        # file exists
        pars = np.load(os.path.join(path_like,"pars.npy"))

        m1, m2, m3 = pars[0], pars[1], pars[2]
        b1, b2, b3 = pars[3], pars[4], pars[5]
        s1, s2, s3 = pars[6], pars[7], pars[8]
        s13 = pars[9]

        kp = pars[12]
        kd = pars[13]

        omega_sel = pars[11]

    else:

        m1, m2, m3 = 0.2, 0.2, 0.2 #masses
        s1, s2, s3, s13 = 200.0, 200.0, 200.0, 200.0 #stiffnesses
        b1, b2, b3 = 0.1, 0.1, 0.1 #viscous damping

        omega_sel = 16.0

        kp = -120.0
        kd = -25.0

    #Mass, damping and stiffness matrices
    MM = np.array([[m1, 0.0, 0.0], [0.0, m2, 0.0], [0.0, 0.0, m3]])
    BB = np.array([[b1+b2, -b2, 0.0], [-b2, b2+b3, -b3], [0.0, -b3, b3]])
    SS = np.array([[s1+s2, -s2, 0.0], [-s2, s2+s3, -s3], [0.0, -s3, s3]])
    Minv = la.inv(MM)

    Freq_list_def = np.load(os.path.join(path_like,"Freq_list_def.npy"))
    Freq_list_up = np.load(os.path.join(path_like,"Freq_list_up.npy"))
    Freq_list_down = np.load(os.path.join(path_like,"Freq_list_down.npy"))
    Amplist_up = np.load(os.path.join(path_like,"Amplist_up.npy"))
    Amplist_down = np.load(os.path.join(path_like,"Amplist_down.npy"))
    Amplist_up2 = np.load(os.path.join(path_like,"Amplist_up2.npy"))
    Amplist_down2 = np.load(os.path.join(path_like,"Amplist_down2.npy"))
    Amplist_up3 = np.load(os.path.join(path_like,"Amplist_up3.npy"))
    Amplist_down3 = np.load(os.path.join(path_like,"Amplist_down3.npy"))
    Exc_amp_list_def = np.load(os.path.join(path_like,"Exc_amp_list_def.npy"))
    Exc_amp_list_incr = np.load(os.path.join(path_like,"Exc_amp_list_incr.npy"))
    Exc_amp_list_decr = np.load(os.path.join(path_like,"Exc_amp_list_decr.npy"))
    Amplist_incr = np.load(os.path.join(path_like,"Amplist_incr.npy"))
    Amplist_decr = np.load(os.path.join(path_like,"Amplist_decr.npy"))
    Amplist_incr2 = np.load(os.path.join(path_like,"Amplist_incr2.npy"))
    Amplist_decr2 = np.load(os.path.join(path_like,"Amplist_decr2.npy"))
    Amplist_incr3 = np.load(os.path.join(path_like,"Amplist_incr3.npy"))
    Amplist_decr3 = np.load(os.path.join(path_like,"Amplist_decr3.npy"))
    branch_cont = np.load(os.path.join(path_like,"branch_cont.npy"))
    IC = np.load(os.path.join(path_like,"IC.npy"))

    Exc_amp_list_incr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_incr.npy"))
    Exc_amp_list_decr_cbc = np.load(os.path.join(path_like,"Exc_amp_list_decr.npy"))
    Amplist_incr_cbc = np.load(os.path.join(path_like,"Amplist_incr.npy"))
    Amplist_decr_cbc = np.load(os.path.join(path_like,"Amplist_decr.npy"))

    cbc_per = np.load(os.path.join(path_like,"cbc_per.npy"))

    mode = request.args.get('value', 0, type=int)

    k = 5

    if mode == 1:
        # Initialise plotted arrays
        #omega_sel = 16.0

        sweep_pars = np.load(os.path.join(path_like,"sweep_pars.npy"))

        Min_exc_amp = sweep_pars[2]
        Max_exc_amp = sweep_pars[3]
        
        Exc_amp_list = np.linspace(Min_exc_amp, Max_exc_amp, 200)

        tend = 100*(2*math.pi/omega_sel)
        tlist = np.linspace(0.0, tend, 50001)

        sol = odeint(cbc2.Open_loop_3st, IC, tlist, args=(np.array([Min_exc_amp, omega_sel]), Minv, BB, SS, s13))

        IC = sol[-1,:]

        tsel = tlist[-501:-1]
        solsel = sol[-501:-1,3]
        solsel2 = sol[-501:-1,4]
        solsel3 = sol[-501:-1,5]

        coeffs0 = cbc2.harm_calc(tsel, solsel, cbc2.trapz, k, omega_sel)
        coeffs02 = cbc2.harm_calc(tsel, solsel2, cbc2.trapz, k, omega_sel)
        coeffs03 = cbc2.harm_calc(tsel, solsel3, cbc2.trapz, k, omega_sel)

        #CBC -bp1

        sol = odeint(cbc2.Open_loop_3st, IC, tlist, args=(np.array([Exc_amp_list[1], omega_sel]), Minv, BB, SS, s13))
        IC = sol[-1,:]
        tsel = tlist[-501:-1]
        solsel = sol[-501:-1,3]
        solsel2 = sol[-501:-1,4]
        solsel3 = sol[-501:-1,5]

        coeffs1 = cbc2.harm_calc(tsel, solsel, cbc2.trapz, k, omega_sel)
        coeffs12 = cbc2.harm_calc(tsel, solsel2, cbc2.trapz, k, omega_sel)
        coeffs13 = cbc2.harm_calc(tsel, solsel3, cbc2.trapz, k, omega_sel)

        branch = np.array([[Exc_amp_list[0], (coeffs0[1]**2+coeffs0[k+2]**2)**0.5, (coeffs02[1]**2+coeffs02[k+2]**2)**0.5, (coeffs03[1]**2+coeffs03[k+2]**2)**0.5],[Exc_amp_list[1], (coeffs1[1]**2+coeffs1[k+2]**2)**0.5, (coeffs12[1]**2+coeffs12[k+2]**2)**0.5, (coeffs13[1]**2+coeffs13[k+2]**2)**0.5]])

        Target_c_list_def = np.linspace(branch[1,1],sweep_pars[4],100)
        np.save(os.path.join(path_like,"Target_c_list_def.npy"), Target_c_list_def)

        Astar1 = 0.0
        Bstar1 = Exc_amp_list[1]
        np.save(os.path.join(path_like,"Astar1.npy"), Astar1)
        np.save(os.path.join(path_like,"Bstar1.npy"), Bstar1)
        np.save(os.path.join(path_like,"IC.npy"), IC)
        np.save(os.path.join(path_like,"branch_cont.npy"), branch)

        coeffs = np.zeros(2*k+2)
        np.save(os.path.join(path_like,"branch_coeffs.npy"), coeffs)

    else:
        pass

    if mode < 100:

        #omega_sel = 16.0

        #Continuation
        #maxit = 200
        #etol = 1e-3
        maxit = np.load(os.path.join(path_like,"cbc_maxiter.npy"))
        etol = np.load(os.path.join(path_like,"cbc_etol.npy"))
        Astar1 = np.load(os.path.join(path_like,"Astar1.npy"))
        Bstar1 = np.load(os.path.join(path_like,"Bstar1.npy"))

        Target_c_list_def = np.load(os.path.join(path_like,"Target_c_list_def.npy"))

        branch_cont = np.load(os.path.join(path_like,"branch_cont.npy"))

        coeffs = np.load(os.path.join(path_like,"branch_coeffs.npy"))

        itn = len(branch_cont)

        Target_c_list = np.array([Target_c_list_def[itn-1]])
        Target_s_list = np.zeros(1)

        IC = np.load(os.path.join(path_like,"IC.npy"))

        branch_cont, IC, Astar1, Bstar1, coeffs = cbc2.continuation(cbc2.CBC_3st,cbc2.trapz,omega_sel,Minv,BB,SS,s13,kp,kd,coeffs,np.zeros(2*k+2),k,branch_cont,IC,Astar1,Bstar1,Target_c_list,Target_s_list,maxit,etol,cbc_per)

        np.save(os.path.join(path_like,"branch_cont.npy"), branch_cont)

        np.save(os.path.join(path_like,"branch_coeffs.npy"), coeffs)

        np.save(os.path.join(path_like,"Astar1.npy"), Astar1)
        np.save(os.path.join(path_like,"Bstar1.npy"), Bstar1)
        np.save(os.path.join(path_like,"IC.npy"), IC)

    else:
        pass

    graph1 = cbc2.cbc_dataplot(Freq_list_up, Freq_list_down, Amplist_up, Amplist_down, Exc_amp_list_incr, Exc_amp_list_decr, Amplist_incr, Amplist_decr, branch_cont, Exc_amp_list_incr_cbc, Exc_amp_list_decr_cbc, Amplist_incr_cbc, Amplist_decr_cbc)

    return graph1



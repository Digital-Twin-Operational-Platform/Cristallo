'''
This function computes the passive and active control laws and shows the kinetic energy of the structure before and after applying these control strategies.
'''
from flask import render_template, request, redirect, url_for
from dtApp import app
from dtApp import date
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import json
# import control.matlab as ctrmat

from dtLib.control.passiveStructure import keoriginal
from dtLib.control.passiveControlTMD import keTMD
from dtLib.control.activeControlVFC import keVFC
from dtLib.control.activeControlVFCmodified import keVFCmod
from dtLib.control.activeControlLQG import keLQG

from dtLib.third_party.python_control_v091.control.ctrlutil import mag2db

@app.route('/control', methods=['GET','POST'])
def control():
    cntrtype = "passive"
    nfs = "1"
    mb = 0.5
    mp = 1
    kp = 1670
    cp = 5
    Bl = 10
    Ze = 8
    h = 5
    wp = 1/(2*np.pi)*np.sqrt(float(kp)/float(mp))
    xip = 100*float(cp)/(2*np.sqrt(float(kp)*float(mp)))
    wpest = 6
    xipest = 100*0.04
    wc = 6
    xic = 100*0.04
    q = 200
    r = 0.1
    Qn = 1.0
    Rn = 10**-12

    Passive = keoriginal()
    freq = Passive['freq']
    T = Passive['ke']
    ITs = Passive['IntKE']

    fig = make_subplots(rows=1, cols=1)
    fig.update_layout(width=583, height=500)
    fig.add_scatter(x=freq,y=T, name='kinetic energy original passive structure', mode = 'lines', row=1, col=1)

    # Update xaxis properties
    fig.update_xaxes(title_text="frequency [Hz]", titlefont=dict(size=14), row=1, col=1)
    fig.update_xaxes(type="log")

    # Update yaxis properties
    fig.update_yaxes(title_text="kinetic energy [dB]", titlefont=dict(size=14), row=1, col=1)
    fig.update_yaxes(range=[-150, 0])

    fig.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))

    kinenergy = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    if request.method=='POST':
        req = request.form
        # print(req)

        cntrtype = req.get("controltype")
        nfs = req.get("controllocation")
        mb = float(req.get("basemass"))
        mp = float(req.get("proofmass"))
        kp = float(req.get("stiffness"))
        cp = float(req.get("damping"))
        Bl = float(req.get("forcefactor"))
        Ze = float(req.get("elimpedance"))
        h = float(req.get("gain"))
        wpest = float(req.get("natfreqest"))
        xipest = float(req.get("dampratioest"))
        wc = float(req.get("natfreqcomp"))
        xic = float(req.get("dampratiocomp"))
        # q = float(req.get("stateweight")) # uncomment when using the LQG approach in server/developer mode
        # r = float(req.get("inputweight")) # uncomment when using the LQG approach in server/developer mode
        # Qn = float(req.get("processcov")) # uncomment when using the LQG approach in server/developer mode
        # Rn = float(req.get("measurementcov")) # uncomment when using the LQG approach in server/developer mode

        wp = 1/(2*np.pi)*np.sqrt(kp/mp)
        xip = 100*cp/(2*np.sqrt(kp*mp))

        if cntrtype=="passive":
            ControlTMD = keTMD(int(nfs), mb, mp, kp, cp)

            freq_TMD = ControlTMD['freq']
            T_TMD = ControlTMD['ke']
            ITstmd = ControlTMD['IntKE']

            RTtmd = ITstmd/ITs
            RTtmd = -(0.5)*mag2db(RTtmd)

            fig.add_scatter(x=freq_TMD,y=T_TMD, name='kinetic energy structure with passive control (TMD)', mode = 'lines', row=1, col=1)
            fig.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))
            kinenergy = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('control.html', controltype=cntrtype, controllocation=nfs, mb=mb, mp=mp, kp=kp, cp=cp, Bl=Bl, Ze=Ze, h=h, wpest=wpest, xipest=xipest, wc=wc, xic=xic, q=q, r=r, Qn=Qn, Rn=Rn, wp="{:.2f}".format(wp), xip="{:.2f}".format(xip), plot=kinenergy, RT="{:.2f}".format(RTtmd),date=date)
        elif cntrtype=="active":
            ControlVFC = keVFC(int(nfs), mb, mp, kp, cp, Bl, Ze, h)

            freq_VFC = ControlVFC['freq']
            T_VFC = ControlVFC['ke']
            ITsvfc = ControlVFC['IntKE']
            IPvfc = ControlVFC['IntCE']
            gm = ControlVFC['Gm']

            RTvfc = ITsvfc/ITs
            RTvfc = -(0.5)*mag2db(RTvfc)

            IPvfc = IPvfc/(Bl**2)*Ze

            if gm>float(1):
                gm = mag2db(gm)
                stab = 'Yes'
            else:
                stab = 'No'
                gm = -float('Inf')

            fig.add_scatter(x=freq_VFC,y=T_VFC, name='kinetic energy structure with active control (DVF)', mode = 'lines', row=1, col=1)
            fig.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))
            kinenergy = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            L_VFC = ControlVFC['ol']
            fig1 = make_subplots(rows=1, cols=1)
            fig1.update_layout(width=583, height=500)
            fig1.add_scatter(x=np.array(float(-1)),y=np.array(float(0)), name='-1+j0 point', mode = 'markers', marker_symbol='cross', marker_size=10, row=1, col=1)
            fig1.add_scatter(x=L_VFC.real,y=L_VFC.imag, name='Nyquist of the open-loop FRF for the Direct Velocity Feedback controller', mode = 'lines', row=1, col=1)
            

            # Update xaxis properties
            fig1.update_xaxes(title_text="Real part", titlefont=dict(size=14), row=1, col=1)
            fig1.update_xaxes(range=[-5, 25])

            # Update yaxis properties
            fig1.update_yaxes(title_text="Imaginary part", titlefont=dict(size=14), row=1, col=1)
            fig1.update_yaxes(range=[-15, 15])

            fig1.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))

            nyquist = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('control.html', controltype=cntrtype, controllocation=nfs, mb=mb, mp=mp, kp=kp, cp=cp, Bl=Bl, Ze=Ze, h=h, wpest=wpest, xipest=xipest, wc=wc, xic=xic, q=q, r=r, Qn=Qn, Rn=Rn, wp="{:.2f}".format(wp), xip="{:.2f}".format(xip), plot=kinenergy, plot1=nyquist, RT="{:.2f}".format(RTvfc), CE="{:.2f}".format(IPvfc), stab=stab, gm="{:.2f}".format(gm),date=date)
        elif cntrtype=="active_dvf_mod":
            ControlVFCmod = keVFCmod(int(nfs), mb, mp, kp, cp, Bl, Ze, h, wpest, xipest, wc, xic)

            freq_VFCmod = ControlVFCmod['freq']
            T_VFCmod = ControlVFCmod['ke']
            ITsvfcmod = ControlVFCmod['IntKE']
            IPvfcmod = ControlVFCmod['IntCE']
            gmmod = ControlVFCmod['Gm']

            RTvfcmod = ITsvfcmod/ITs
            RTvfcmod = -(0.5)*mag2db(RTvfcmod)

            IPvfcmod = IPvfcmod/(Bl**2)*Ze

            if gmmod>float(1):
                gmmod = mag2db(gmmod)
                stabmod = 'Yes'
            else:
                stabmod = 'No'
                gmmod = -float('Inf')

            fig.add_scatter(x=freq_VFCmod,y=T_VFCmod, name='kinetic energy structure with active control (DVF+EC)', mode = 'lines', row=1, col=1)
            fig.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))
            kinenergy = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            L_VFCmod = ControlVFCmod['ol']
            fig1 = make_subplots(rows=1, cols=1)
            fig1.update_layout(width=583, height=500)
            fig1.add_scatter(x=np.array(float(-1)),y=np.array(float(0)), name='-1+j0 point', mode = 'markers', marker_symbol='cross', marker_size=10, row=1, col=1)
            fig1.add_scatter(x=L_VFCmod.real,y=L_VFCmod.imag, name='Nyquist of the open-loop FRF for the modified Direct Velocity Feedback controller', mode = 'lines', row=1, col=1)
            

            # Update xaxis properties
            fig1.update_xaxes(title_text="Real part", titlefont=dict(size=14), row=1, col=1)
            fig1.update_xaxes(range=[-5, 25])

            # Update yaxis properties
            fig1.update_yaxes(title_text="Imaginary part", titlefont=dict(size=14), row=1, col=1)
            fig1.update_yaxes(range=[-15, 15])

            fig1.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))

            nyquist = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('control.html', controltype=cntrtype, controllocation=nfs, mb=mb, mp=mp, kp=kp, cp=cp, Bl=Bl, Ze=Ze, h=h, wpest=wpest, xipest=xipest, wc=wc, xic=xic, q=q, r=r, Qn=Qn, Rn=Rn, wp="{:.2f}".format(wp), xip="{:.2f}".format(xip), plot=kinenergy, plot1=nyquist, RT="{:.2f}".format(RTvfcmod), CE="{:.2f}".format(IPvfcmod), stab=stabmod, gm="{:.2f}".format(gmmod),date=date)
        elif cntrtype=="active_lqg":
            ControlLQG = keLQG(int(nfs), mb, mp, kp, cp, Bl, Ze, q, r, Qn, Rn)

            freq_LQG = ControlLQG['freq']
            T_LQG = ControlLQG['ke']
            ITsLQG = ControlLQG['IntKE']
            IPLQG = ControlLQG['IntCE']
            gmLQG = ControlLQG['Gm']

            RTLQG = ITsLQG/ITs
            RTLQG = -(0.5)*20*np.log10(RTLQG) # RTLQG = -(0.5)*ctrmat.mag2db(RTLQG)

            IPLQG = IPLQG/(Bl**2)*Ze

            if gmLQG>float(1):
                gmLQG = mag2db(gmLQG)
                stabLQG = '--'
            else:
                stabLQG = '--'
                gmLQG = -float('Inf')

            fig.add_scatter(x=freq_LQG,y=T_LQG, name='kinetic energy structure with active control (LQG)', mode = 'lines', row=1, col=1)
            fig.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))
            kinenergy = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            L_LQG = ControlLQG['ol']
            fig1 = make_subplots(rows=1, cols=1)
            fig1.update_layout(width=583, height=500)
            fig1.add_scatter(x=np.array(float(-1)),y=np.array(float(0)), name='-1+j0 point', mode = 'markers', marker_symbol='cross', marker_size=10, row=1, col=1)
            fig1.add_scatter(x=L_LQG.real,y=L_LQG.imag, name='Nyquist of the open-loop FRF for the Linear-Quadratic Gaussian regulator', mode = 'lines', row=1, col=1)
            

            # Update xaxis properties
            fig1.update_xaxes(title_text="Real part", titlefont=dict(size=14), row=1, col=1)
            fig1.update_xaxes(range=[-5, 25])

            # Update yaxis properties
            fig1.update_yaxes(title_text="Imaginary part", titlefont=dict(size=14), row=1, col=1)
            fig1.update_yaxes(range=[-15, 15])

            fig1.update_layout(showlegend=True, font=dict(size=14), legend=dict(x=-.1, y=1.2))

            nyquist = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('control.html', controltype=cntrtype, controllocation=nfs, mb=mb, mp=mp, kp=kp, cp=cp, Bl=Bl, Ze=Ze, h=h, wpest=wpest, xipest=xipest, wc=wc, xic=xic, q=q, r=r, Qn=Qn, Rn=Rn, wp="{:.2f}".format(wp), xip="{:.2f}".format(xip), plot=kinenergy, plot1=nyquist, RT="{:.2f}".format(RTLQG), CE="{:.2f}".format(IPLQG), stab=stabLQG, gm="--",date=date)
        else:
            return render_template('control.html', controltype=cntrtype, controllocation=nfs, mb=mb, mp=mp, kp=kp, cp=cp, Bl=Bl, Ze=Ze, h=h, wpest=wpest, xipest=xipest, wc=wc, xic=xic, q=q, r=r, Qn=Qn, Rn=Rn, wp="{:.2f}".format(wp), xip="{:.2f}".format(xip), plot=kinenergy,date=date)
    return render_template('control.html', controltype=cntrtype, controllocation=nfs, mb=mb, mp=mp, kp=kp, cp=cp, Bl=Bl, Ze=Ze, h=h, wpest=wpest, xipest=xipest, wc=wc, xic=xic, q=q, r=r, Qn=Qn, Rn=Rn, wp="{:.2f}".format(wp), xip="{:.2f}".format(xip), plot=kinenergy,date=date)
   

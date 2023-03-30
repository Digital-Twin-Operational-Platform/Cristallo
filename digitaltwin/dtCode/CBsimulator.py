'''

`dtApp/dtCode/threedof.py`


:Authors: 
    David J Wagg, University of Sheffield
    Marco De Angelis, University of Liverpool
    

:Created: December 2021
:Edited:  January 2022


:Copyright: 
    BSD Licence



This python file ``simulator.py`` is the backend code for the simulator page.

This module is intended to be self-contained, thus it only depends on the scientific module dtLib/simulator/*, which generates modal data for 3DOF system using numerical integration

 
Currently this is for simulating an impact hammer excitation of a 3DOF (non)linear mass-spring system
The impact force is applied to Mass 1, and random initial conditions are also applied to the displacements
The parameters are ICs are selected from Gaussian distributions at the start of each time series simulation.
The mean and standard deviations for the Gaussians can be defined in the code.

The results for N sets of displacement time series are put into the numpy array xs. Plots are produced to give a visual check.

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

# Import external packages
from flask import render_template, request
import numpy
import os
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Import internal packages
from digitaltwin.dtLib.simulator import CBthreedof
from digitaltwin.dtLib import classes
from digitaltwin import date

SLIDER_SCALE = 10000

PLOT_DEFINITION = 350

PLOT_WIDTH = 600
PLOT_HEIGHT = 800

W_PLOT_RANGE = [5, 200]

def CBsimula():  # Properties displayed on landing
    '''
    Although this function takes explicit inputs, it is responsible for dispatching the data requests from the html page. 

    The html inputs are dispathed from the Flask's request object ``request``, as follows:

    .. code-block:: python

         for key,val in request.form.items():
            if key == "input1":
                input1 = int(val)
            if key == 'input2':
                input2 = float(val)

    '''
    # Prepare for plotting with Plotly:
    fig = make_subplots(rows=3, cols=1, subplot_titles=(
        "Bottom Floor", "Middle FLoor", "Top Floor"), shared_xaxes=False)
    fig.update_layout(width=PLOT_WIDTH, height=PLOT_HEIGHT)
    fig2 = make_subplots(rows=3, cols=1, subplot_titles=(
        "Bottom Floor", "Middle FLoor", "Top Floor"), shared_xaxes=False)
    fig2.update_layout(width=PLOT_WIDTH, height=PLOT_HEIGHT)
    dir = os.path.join("digitaltwin","dtData","profiles","default.json")
    model = classes.MODEL3DOF()
    model.fromJSON(dir)
    Defaults = {}
    Defaults["N"], Defaults["T"], Defaults["Sf"], Defaults["Excite"] = 1, 5.0, 2048, "Hammer"
    Defaults["Ix"], Defaults["Iv"] = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    Defaults["D_init"] =  [0.0, 0.0]

    if request.method == 'POST':
        if 'JSON' in request.files:
            # Save to file
            file = request.files["JSON"]
            filename = file.filename
            file_path = os.path.join("digitaltwin","dtData","profiles",filename)
            file.save(file_path)
            # Update model class with JSON
            model.fromJSON(file_path)
            model.souce=f"From Profile {filename}"
            timeplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            freqplot = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template("CB-Simulator.html", model = model, Defaults=Defaults, timeplot=timeplot, freqplot=freqplot, Sf=0,date=date)
        else:
            for key, val in request.form.items():
                if key == "MC_samples":
                    N, Defaults["N"] = int(val), int(val)
                if key == "Excite":
                    Defaults["Excite"] = val
                if key == "Time":
                    Defaults["T"] = float(val)
                if key == "SFreq":
                    Defaults["Sf"] = int(val)
                if key == "mass1":
                    m1 = float(val)
                if key == "mass2":
                    m2 = float(val)
                if key == "mass3":
                    m3 = float(val)
                if key == "massD":
                    disp_m = float(val)
                if key == "stiff1":
                    k1 = float(val)
                if key == "stiff2":
                    k2 = float(val)
                if key == "stiff3":
                    k3 = float(val)
                if key == "stiffD":
                    disp_k = float(val)
                if key == "damp1":
                    c1 = float(val)
                if key == "damp2":
                    c2 = float(val)
                if key == "damp3":
                    c3 = float(val)
                if key == "dampD":
                    disp_c = float(val)
                if key == "x1":
                    Defaults["Ix"][0] = float(val)
                if key == "x2":
                    Defaults["Ix"][1] = float(val)
                if key == "x3":
                    Defaults["Ix"][2] = float(val)
                if key == "xD":
                    Defaults["D_init"][0] = float(val)
                if key == "v1":
                    Defaults["Iv"][0] = float(val)
                if key == "v2":
                    Defaults["Iv"][1] = float(val)
                if key == "v3":
                    Defaults["Iv"][2] = float(val)
                if key == "vD":
                    Defaults["D_init"][1] = float(val)
            model = classes.MODEL3DOF(M=[m1,m2,m3],K=[k1,k2,k3],C=[c1,c2,c3],dispersion=[disp_m,disp_k,disp_c],source="user")
            file_path = os.path.join("digitaltwin","dtData","profiles","user_submitted.json")
            model.toJSON(file_path)
        Defaults["S"] = int(Defaults["T"]*Defaults["Sf"])
        # assign values to produce plots anyway
        x_list = CBthreedof.CBsimulator(model,Defaults)

        for i in range(N):
            fig.add_trace(go.Scatter(name='', x=x_list[i][0].time, y=x_list[i][0].response,
                                     fill=None,
                                     mode='lines',
                                     line_color='indigo',
                                     opacity=.3,
                                     showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(name='', x=x_list[i][1].time, y=x_list[i][1].response,
                                     fill=None,
                                     mode='lines',
                                     line_color='indigo',
                                     opacity=.3,
                                     showlegend=False), row=2, col=1)
            fig.add_trace(go.Scatter(name='', x=x_list[i][2].time, y=x_list[i][2].response,
                                     fill=None,
                                     mode='lines',
                                     line_color='indigo',
                                     opacity=.3,
                                     showlegend=False), row=3, col=1)
            x_list[i][0].PSD()
            fig2.add_trace(go.Scatter(name='', x=x_list[i][0].psd_freq, y=numpy.log10(x_list[i][0].psd_resp),
                                      fill=None,
                                      mode='lines',
                                      line_color='indigo',
                                      opacity=.3,
                                      showlegend=False), row=1, col=1)
            x_list[i][1].PSD()                         
            fig2.add_trace(go.Scatter(name='', x=x_list[i][1].psd_freq, y=numpy.log10(x_list[i][1].psd_resp),
                                      fill=None,
                                      mode='lines',
                                      line_color='indigo',
                                      opacity=.3,
                                      showlegend=False), row=2, col=1)
            x_list[i][2].PSD()
            fig2.add_trace(go.Scatter(name='',  x=x_list[i][2].psd_freq, y=numpy.log10(x_list[i][2].psd_resp),
                                      fill=None,
                                      mode='lines',
                                      line_color='indigo',
                                      opacity=.3,
                                      showlegend=False), row=3, col=1)

        fig.update_layout(title_text="",
                          showlegend=True,
                          font=dict(size=14),
                          plot_bgcolor='rgba(0, 0, 0, 0.1)', paper_bgcolor='rgba(0, 0, 0, 0)')  # paper_bgcolor= 'rgba(0, 0, 0, 0.05)'

        fig.update_xaxes(title_text='Time (s)', title_font={"size": 11})
        fig.update_yaxes(title_text='Displacement (m)',
                         title_font={"size": 11})

        timeplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        fig2.update_layout(title_text="",
                           showlegend=True,
                           font=dict(size=14),
                           plot_bgcolor='rgba(0, 0, 0, 0.1)', paper_bgcolor='rgba(0, 0, 0, 0)')  # paper_bgcolor= 'rgba(0, 0, 0, 0.05)'

        fig2.update_xaxes(title_text='Frequency (Hz)', title_font={"size": 11})
        # fig2.update_yaxes(title_text='Spectral density (DB)',title_font={"size":11},type="log")
        fig2.update_yaxes(title_text='Spectral density (DB)',
                          title_font={"size": 11})

        freqplot = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("CB-Simulator.html", model = model, Defaults=Defaults, timeplot=timeplot, freqplot=freqplot, Sf=Defaults["Sf"],date=date)
    else:
        timeplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        freqplot = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template("CB-Simulator.html", model = model, Defaults=Defaults, timeplot=timeplot, freqplot=freqplot, Sf=0,date=date)

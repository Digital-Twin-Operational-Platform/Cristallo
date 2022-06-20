'''

`dtApp/dtCode/simulator_1dof.py`

'''

# Import external packages
from flask import render_template, request, redirect, Response, url_for
import importlib.util
import numpy
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Import internal packages
from dtApp import app
from dtApp import date
from dtLib.simulator import onedof

M = onedof.M
K = onedof.K
C = onedof.C

DISP_init = onedof.DISP_init   # Initial displacement
VELO_init = onedof.VELO_init   # Initial velocity
# INIT = [DISP_init,VELO_init]

F = onedof.F   # Intensity of impact force
T = onedof.T # [s] observation time

STEP_SIZE = onedof.STEP_SIZE # 0.0001 # [s] 

DURATION = onedof.DURATION #0.01 # [s]
AT = onedof.AT # 0.05 # [s]


SLIDER_SCALE = 10000

PLOT_DEFINITION = 350

PLOT_WIDTH = 600
PLOT_HEIGHT = 800

Defaults = onedof.DATA

# Defaults={
#     'M': M,
#     'K': K,
#     'C': C,
#     'DISP_init': DISP_init,
#     'VELO_init': VELO_init,
#     'F': F,
#     'T': T,
#     'STEP_SIZE':STEP_SIZE,
#     'DURATION': DURATION,
#     'AT': AT

# }

@app.route('/simulator_1dof', methods=['GET','POST'])
def backend(): # Properties displayed on landing
    '''
    Description goes here..
    '''
    data = Defaults
    # Prepare for plotting with Plotly:
    fig = make_subplots(rows=2, cols=1, subplot_titles=("Displacement", "Hammer force"), shared_xaxes=False)
    fig.update_layout(width=PLOT_WIDTH, height=PLOT_HEIGHT) 
    fig2= make_subplots(rows=1, cols=1, subplot_titles=("FRF",), shared_xaxes=False)
    fig2.update_layout(width=PLOT_WIDTH, height=PLOT_HEIGHT) 
    if request.method=='POST':
        for key,val in request.form.items():
            if key == "Time":  data["T"] = float(val)
            if key == "mass":  data["M"] = float(val)
            if key == "stiff": data["K"] = float(val)
            if key == "damp":  data["C"] = float(val)
            if key == "x":  data["DISP_init"] = float(val)
            if key == "v":  data["VELO_init"] = float(val)
            if key == 'force': data['F'] = float(val)
            if key == 'at': data['AT']=float(val)
            if key == 'duration': data['DURATION'] = float(val)
            if key == 'step_size': data['STEP_SIZE'] = float(val)

        # assign values to produce plots anyway
        tt,xx,fo = onedof.msd_simulator(data)
        fr,Pxx = onedof.fourier_transform(tt,xx,data)
    
        fig.add_trace(go.Scatter(name='',x=tt, y=xx[:, 1],    
                        fill=None,
                        mode='lines',
                        line_color='indigo',
                        opacity = .3,
                        showlegend=False),row=1,col=1)
        fig.add_trace(go.Scatter(name='',x=tt, y=fo,
                        fill=None,
                        mode='lines',
                        line_color='indigo',
                        opacity = .3,
                        showlegend=False),row=2,col=1)
        fig2.add_trace(go.Scatter(name='',x=fr, y=Pxx,    
                        fill=None,
                        mode='lines',
                        line_color='indigo',
                        opacity = .3,
                        showlegend=False),row=1,col=1)
    
        fig.update_layout(title_text="",\
                showlegend=True,\
                font=dict(size=14),\
                plot_bgcolor= 'rgba(0, 0, 0, 0.1)',paper_bgcolor= 'rgba(0, 0, 0, 0)') #paper_bgcolor= 'rgba(0, 0, 0, 0.05)'
    
        fig.update_xaxes(title_text='Time (s)',title_font={"size":11})
        fig.update_yaxes(title_text='Displacement (m)',title_font={"size":11})
    
        timeplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
        fig2.update_layout(title_text="",\
            showlegend=True,\
            font=dict(size=14),\
            plot_bgcolor= 'rgba(0, 0, 0, 0.1)',paper_bgcolor= 'rgba(0, 0, 0, 0)') #paper_bgcolor= 'rgba(0, 0, 0, 0.05)'
    
        fig2.update_xaxes(title_text='Frequency (Hz)',title_font={"size":11})
        fig2.update_yaxes(title_text='Frequency response (DB)',title_font={"size":11})
    
        freqplot = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
        return render_template("simulator_1dof.html",Data=data,timeplot=timeplot,freqplot=freqplot)
    else:
        timeplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        freqplot = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template("simulator_1dof.html",Data=Defaults,timeplot=timeplot,freqplot=freqplot)
'''

`dtApp/dtCode/unquant.py`


:Author: 
    Marco De Angelis

:Organisation: 
    University of Liverpool

:Copyright: 
    BSD Licence

This single python file ``unquant.py`` is the backend code for the uncertainty page.

A single function ``unquant()`` wrangles all the data requests from the html template. 
The function takes care of the data sent by user performing a few actions:

* The data is converted in SI units;
* The slider position is converted to an interval;
* The uncertainty propagation function is invoked;
* The output is captured and plotted with Plotly.

This file makes sure that when no data are provided by the user, the page displays and plots the nominal values.

The default values that populate the page on load are defined at the top of document as persistent variables.

.. code-block:: python

    MASS = [5.362, 5.144,  5.142]            # *1e4 kg

    STFF = [3.846, 4.464, 4.589]             # *1e8 N/m

    DAMP = [1.699, 1.016, 1.34]              # *1e4 Ns/m


This page makes use of the following dependencies.

External dependencies 

.. code-block:: python

    from flask import render_template, request, redirect, Response, url_for
    import importlib.util
    import numpy
    import plotly
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import json


The internal dependency is imported from the scientific code library.

.. code-block:: python

    import dtLib.unquant.msd3 as msd3





If not otherwise specified: 

|    * The excitation is applied at floor 2. 
|    * The frequency range is [5,200] Hz.
|    * The FRF plots 350 frequencies.
|    * The number of MonteCarlo samples is 50.

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
import dtLib.unquant.msd3 as msd3


M_INP_1, M_INP_2, M_INP_3 = 5.36, 5.14, 5.14
K_INP_1, K_INP_2, K_INP_3 = 3.85, 4.46, 4.59
C_INP_1, C_INP_2, C_INP_3 = 1.70, 1.02, 1.34

SLIDER_SCALE = 10000

PLOT_DEFINITION = 350

PLOT_WIDTH = 900
PLOT_HEIGHT = 800

W_PLOT_RANGE = [5,200]

@app.route('/unquant', methods=['GET','POST'])
def unquant(): # Properties displayed on landing
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
    M_inp_1, M_inp_2, M_inp_3 = M_INP_1, M_INP_2, M_INP_3
    eM_slider_1, eM_slider_2, eM_slider_3 = 0,0,0
    K_inp_1, K_inp_2, K_inp_3 = K_INP_1, K_INP_2, K_INP_3
    eK_slider_1,eK_slider_2,eK_slider_3 = 0,0,0
    C_inp_1, C_inp_2, C_inp_3 = C_INP_1, C_INP_2, C_INP_3
    eC_slider_1, eC_slider_2, eC_slider_3 = 0,0,0
    MCsamp = 50
    maxUnc = int(10) # percent
    Exci = '2' # excitation at floor 2
    if request.method=='POST':
        fig = make_subplots(rows=3, cols=1, subplot_titles=("Floor 3", "Floor 2", "Floor 1"), shared_xaxes=False)
        fig.update_layout(width=PLOT_WIDTH, height=PLOT_HEIGHT) 
        for key,val in request.form.items():
            if key == "maxU":
                maxUnc = int(val)
            if key == 'exci':
                Exci = val
            # Mass
            if key == "M_centre_3":
                M_inp_3 = float(val)
            if key == "M_centre_2":
                M_inp_2 = float(val)
            if key == "M_centre_1":
                M_inp_1 = float(val)
            if  key == "eM_slider_3":
                eM_slider_3 = float(val)  
            if  key == "eM_slider_2":
                eM_slider_2 = float(val)
            if  key == "eM_slider_1":
                eM_slider_1 = float(val)
            # Stiff
            if key == "K_centre_3":
                K_inp_3 = float(val)
            if key == "K_centre_2":
                K_inp_2 = float(val)
            if key == "K_centre_1":
                K_inp_1 = float(val)
            if key == "eK_slider_3":
                eK_slider_3 = float(val)  
            if key == "eK_slider_2":
                eK_slider_2 = float(val)  
            if key == "eK_slider_1":
                eK_slider_1 = float(val)  
            # Damp
            if key == "C_centre_3":
                C_inp_3 = float(val)
            if key == "C_centre_2":
                C_inp_2 = float(val)
            if key == "C_centre_1":
                C_inp_1 = float(val)
            if key == "eC_slider_3":
                eC_slider_3 = float(val)
            if key == "eC_slider_2":
                eC_slider_2 = float(val)
            if key == "eC_slider_1":
                eC_slider_1 = float(val)
            if key == "MC_samples":
                MCsamp = int(val)
            if key == "Subintervals":
                Subintervals = val
       
        def Lo(c,e):
            '''
            Function retrieving the lower bound of an interval provided in central notation.

            :param c: Midpoint of the interval
            :param e:   Relative half-width of the interval 

            :returns: The lower bound of the interval
            '''
            return c * (1-e)
        def Hi(c,e):
            '''
            Function retrieving the lower bound of an interval provided in central notation.

            :param c:   Midpoint of the interval
            :param e:   Relative half-width of the interval 

            :returns: The upper bound of the interval
            '''
            return c * (1+e)

        M_inp = [M_inp_1, M_inp_2, M_inp_3]
        M_inp_SI = [1e4 * mi for mi in M_inp]
        M_slider = [eM_slider_1,eM_slider_2,eM_slider_3]
        M_e = [float(ms) * maxUnc / SLIDER_SCALE for ms in M_slider] 
        mI = [[Lo(m,e), Hi(m,e)] for m,e in zip(M_inp_SI,M_e)]

        K_inp = [ K_inp_1, K_inp_2, K_inp_3]
        K_inp_SI = [1e8 * ki for ki in K_inp]
        K_slider = [eK_slider_1,eK_slider_2,eK_slider_3]
        K_e = [ks * maxUnc / SLIDER_SCALE for ks in K_slider] 
        kI = [[Lo(k,e), Hi(k,e)] for k,e in zip(K_inp_SI,K_e)]

        C_inp = [ C_inp_1, C_inp_2, C_inp_3]
        C_inp_SI = [1e4 * ci for ci in C_inp]
        C_slider = [eC_slider_1,eC_slider_2,eC_slider_3]
        C_e = [cs * maxUnc / SLIDER_SCALE for cs in C_slider] 
        cI = [[Lo(c,e), Hi(c,e)] for c,e in zip(C_inp_SI,C_e)]
        

        U = sum([em + ek + ec for em,ek,ec in zip(M_e,K_e,C_e)])
        uncertainty = True
        if abs(U)<1e-5:
            uncertainty = False

        if uncertainty:
            kwargs = { # inputs required by the library module
                'w_range':W_PLOT_RANGE,
                'mI':mI,
                'kI':kI,
                'cI':cI,
                'exci_floor':Exci,
                }

            kwargs['n1'] = 200
            kwargs['n2'] = 30
            ww,Y_cart = msd3.displacement_bounds_cartesian_MK(**kwargs) 
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_cart)[:,0,0],
                            fill=None,
                            mode='lines',
                            line_color='indigo',
                            showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_cart)[:,1,0],
                            fill=None,
                            mode='lines',
                            line_color='indigo',
                            showlegend=False), row=2, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_cart)[:,2,0],
                            fill=None,
                            mode='lines',
                            line_color='indigo',
                            showlegend=False), row=3, col=1)
            
            fig.add_trace(go.Scatter(name='Cartesian',x=ww, y=numpy.log10(Y_cart)[:,0,1],
                            fill='tonexty',
                            mode='lines',
                            line_color='indigo'), row=1, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_cart)[:,1,1],
                            fill='tonexty',
                            mode='lines',
                            line_color='indigo',
                            showlegend=False), row=2, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_cart)[:,2,1],
                            fill='tonexty',
                            mode='lines',
                            line_color='indigo',
                            showlegend=False), row=3, col=1)

            kwargs['n1'] = 200
            kwargs['n2'] = MCsamp

            ww,Y_in = msd3.displacement_bounds_montecarlo(**kwargs) 
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_in)[:,0,0],
                            fill=None,
                            mode='lines',
                            line_color='limegreen',
                            showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_in)[:,1,0], 
                            fill=None,
                            mode='lines',
                            line_color='limegreen',
                            showlegend=False), row=2, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_in)[:,2,0],
                            fill=None,
                            mode='lines',
                            line_color='limegreen',
                            showlegend=False), row=3, col=1)

            fig.add_trace(go.Scatter(name='MonteCarlo',x=ww, y=numpy.log10(Y_in)[:,0,1],
                            fill='tonexty',
                            mode='lines',
                            line_color='limegreen'), row=1, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_in)[:,1,1],
                            fill='tonexty',
                            mode='lines',
                            line_color='limegreen',
                            showlegend=False), row=2, col=1)
            fig.add_trace(go.Scatter(name='',x=ww, y=numpy.log10(Y_in)[:,2,1],
                            fill='tonexty',
                            mode='lines',
                            line_color='limegreen',
                            showlegend=False), row=3, col=1)

        # Case without uncertainty
        kwargs = { # inputs required by the library module
            'w_range':W_PLOT_RANGE,
            'm':M_inp_SI,
            'k':K_inp_SI,
            'c':C_inp_SI,
            'n':PLOT_DEFINITION,
            'exci_floor':Exci,
        }
        ww,Y_pr = msd3.displacement_msd_numpy_abs_ww(**kwargs) 
        fig.add_trace(go.Scatter(name = 'Nominal',x=ww, y=numpy.log10(Y_pr)[:,0],line_color='orangered'), row=1, col=1)
        fig.add_trace(go.Scatter(x=ww, y=numpy.log10(Y_pr)[:,1],line_color='orangered',showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=ww, y=numpy.log10(Y_pr)[:,2],line_color='orangered',showlegend=False), row=3, col=1)    
        
        # Update xaxis properties
        fig.update_xaxes(title_text='[Hz]', titlefont=dict(size=14), row=3, col=1) # fig.update_xaxes(type="log")
        fig.update_yaxes(title_text='[dB]', titlefont=dict(size=14), row=1, col=1)
        fig.update_yaxes(title_text='[dB]', titlefont=dict(size=14), row=2, col=1)
        fig.update_yaxes(title_text='[dB]', titlefont=dict(size=14), row=3, col=1)
        # fig.update_yaxes(range=[-150, 0])
        fig.update_layout(title_text="Bounds on displacement Frequency Response Function (FRF)",\
        showlegend=True,\
        font=dict(size=14),\
        plot_bgcolor= 'rgba(0, 0, 0, 0.1)',paper_bgcolor= 'rgba(0, 0, 0, 0)') #paper_bgcolor= 'rgba(0, 0, 0, 0.05)'

        sideplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        def Lo(inp,e):
            return inp * (1-e)
        def Hi(inp,e):
            return inp * (1+e)

        M_lo = [Lo(mi,me) for mi,me in zip(M_inp,M_e)]#, Lo(M_inp_2,M_e), Lo(M_inp_3,M_e)]
        M_hi = [Hi(mi,me) for mi,me in zip(M_inp,M_e)]#, Hi(M_inp_2,M_e), Hi(M_inp_3,M_e)]
        K_lo = [Lo(ki,ke) for ki,ke in zip(K_inp,K_e)]#[Lo(K_inp_1,K_e), Lo(K_inp_2,K_e), Lo(K_inp_3,K_e)]
        K_hi = [Hi(ki,ke) for ki,ke in zip(K_inp,K_e)]#[Lo(K_inp_1,K_e), Lo(K_inp_2,K_e), Lo(K_inp_3,K_e)]
        C_lo = [Lo(ci,ce) for ci,ce in zip(C_inp,C_e)]#C_lo = [Lo(C_inp_1,C_e), Lo(C_inp_2,C_e), Lo(C_inp_3,C_e)]
        C_hi = [Hi(ci,ce) for ci,ce in zip(C_inp,C_e)]#C_hi = [Hi(C_inp_1,C_e), Hi(C_inp_2,C_e), Hi(C_inp_3,C_e)]

        M_val = [float(M_inp_1), float(M_inp_2), float(M_inp_3)]
        K_val = [float(K_inp_1), float(K_inp_2), float(K_inp_3)]
        C_val = [float(C_inp_1), float(C_inp_2), float(C_inp_3)]

        return render_template("unquant.html", UNC = maxUnc, MCsamp=MCsamp, \
            M_val = M_val, M_e = M_e, M_slider = M_slider,  M_lo = M_lo, M_hi = M_hi,\
            K_val = K_val, K_e = K_e, K_slider = K_slider, K_lo = K_lo, K_hi = K_hi,\
            C_val = C_val, C_e = C_e, C_slider = C_slider, C_lo = C_lo, C_hi = C_hi,\
            Exci = Exci, plot = sideplot,date=date) #, \
    else: # on page re-load and landing
        fig = make_subplots(rows=3, cols=1, subplot_titles=("Floor 3", "Floor 2", "Floor 1"),shared_xaxes=False)
        fig.update_layout(width=PLOT_WIDTH, height=PLOT_HEIGHT)    

        M_inp = [M_inp_1, M_inp_2, M_inp_3]
        M_inp_SI = [1e4 * mi for mi in M_inp]
        K_inp = [ K_inp_1, K_inp_2, K_inp_3]
        K_inp_SI = [1e8 * ki for ki in K_inp]
        C_inp = [ C_inp_1, C_inp_2, C_inp_3]
        C_inp_SI = [1e4 * ci for ci in C_inp]

        kwargs = { # inputs required by the library module
            'w_range':W_PLOT_RANGE,
            'm':M_inp_SI,
            'k':K_inp_SI,
            'c':C_inp_SI,
            'n':PLOT_DEFINITION,
            'exci_floor':Exci,
        }

        ww,Y_pr = msd3.displacement_msd_numpy_abs_ww(**kwargs) 

        fig.add_scatter(x=ww, y=numpy.log10(Y_pr)[:,0], name='', mode = 'lines', row=1, col=1)
        fig.add_scatter(x=ww, y=numpy.log10(Y_pr)[:,1], name='', mode = 'lines', row=2, col=1)
        fig.add_scatter(x=ww, y=numpy.log10(Y_pr)[:,2], name='', mode = 'lines', row=3, col=1)

        # Update xaxis properties
        fig.update_xaxes(title_text='Frequency [Hz]', titlefont=dict(size=14), row=3, col=1)
        fig.update_yaxes(title_text='[dB]', titlefont=dict(size=14), row=1, col=1)
        fig.update_yaxes(title_text='[dB]', titlefont=dict(size=14), row=2, col=1)
        fig.update_yaxes(title_text='[dB]', titlefont=dict(size=14), row=3, col=1)

        fig.update_layout(title_text="Bounds on displacement Frequency Response Function (FRF)",\
        showlegend=False,\
        font=dict(size=14),\
        plot_bgcolor= 'rgba(0, 0, 0, 0.1)', paper_bgcolor= 'rgba(0, 0, 0, 0.0)')
        
        sideplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        M_val = [float(M_INP_1), float(M_INP_2), float(M_INP_3)]
        K_val = [float(K_INP_1), float(K_INP_2), float(K_INP_3)]
        C_val = [float(C_INP_1), float(C_INP_2), float(C_INP_3)]
        return render_template("unquant.html", UNC = maxUnc, MCsamp=MCsamp,\
            M_val = M_val, M_e = [0]*3, M_slider = [0]*3, M_lo = M_val, M_hi = M_val,\
            K_val = K_val, K_e = [0]*3, K_slider = [0]*3, K_lo = K_val, K_hi = K_val,\
            C_val = C_val, C_e = [0]*3, C_slider = [0]*3, C_lo = C_val, C_hi = C_val,\
            Exci=Exci, plot=sideplot,date=date)
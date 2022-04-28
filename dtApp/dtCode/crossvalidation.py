'''
This function compares the experimental FRFs of each structure with the simulated FRFs of their respective numerical models.
'''
from flask import render_template
from dtApp import app
from dtApp import date

import plotly
from plotly.subplots import make_subplots
import numpy as np
import json

from dtLib.crossval.extract_data import tSW,tSO,tSH,tBR,youtSW,youtSO,youtSH,youtBR
from dtLib.crossval.extract_data import tNumSW,tNumSWmiddle,tNumSO,tNumSH,tNumBR,tNumSHmiddle,youtNumSW,youtNumSO,youtNumSH,youtNumBR

@app.route('/crossval')#@app.route('/ExpValidation_Updated')
def ExpValidation_Updated():
    return render_template('crossvalidation.html',date=date)


@app.route('/crossval_1')
def Exp_Data():
    """
    This function gathers the experimental data and displays them.
    """
    # Figure1
    fig1 = make_subplots(rows=2, cols=2,vertical_spacing=0.15,
    subplot_titles=("<b>Prototype 1<b>","<b>Prototype 2<b>", "<b>Prototype 3<b>", "<b>Prototype 4<b>"))

    # Fig1.a
    fig1.add_scatter(x=tSW,y=youtSW[:,0], name='Acc floor 1', mode = 'lines', row=1, col=1)
    fig1.add_scatter(x=tSW,y=youtSW[:,1], name='Acc floor 2', mode = 'lines', row=1, col=1)
    fig1.add_scatter(x=tSW,y=youtSW[:,2], name='Acc floor 3', mode = 'lines', row=1, col=1)
    # Update xaxis properties
    fig1.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=1, col=1)
    # Update yaxis properties
    fig1.update_yaxes(title_text="dB", titlefont=dict(size=15), row=1, col=1)

    ## Fig1.b
    fig1.add_scatter(x=tSO,y=youtSO[:,0], name='Acc floor 1', mode = 'lines', row=1, col=2)
    fig1.add_scatter(x=tSO,y=youtSO[:,1], name='Acc floor 2', mode = 'lines', row=1, col=2)
    fig1.add_scatter(x=tSO,y=youtSO[:,2], name='Acc floor 3', mode = 'lines', row=1, col=2)
    # Update xaxis properties
    fig1.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=1, col=2)
    # Update yaxis properties
    fig1.update_yaxes(title_text="dB", titlefont=dict(size=15), row=1, col=2)

    #Fig1.c
    fig1.add_scatter(x=tSH,y=youtSH[:,0], name='Acc floor 1', mode = 'lines', row=2, col=1)
    fig1.add_scatter(x=tSH,y=youtSH[:,1], name='Acc floor 2', mode = 'lines', row=2, col=1)
    fig1.add_scatter(x=tSH,y=youtSH[:,2], name='Acc floor 3', mode = 'lines', row=2, col=1)
    # Update xaxis properties
    fig1.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=2, col=1)
    # Update yaxis properties
    fig1.update_yaxes(title_text="dB", titlefont=dict(size=15), row=2, col=1)

    #Fig1.d
    fig1.add_scatter(x=tBR,y=youtBR[:,0], name='Acc floor 1', mode = 'lines', row=2, col=2)
    fig1.add_scatter(x=tBR,y=youtBR[:,1], name='Acc floor 2', mode = 'lines', row=2, col=2)
    fig1.add_scatter(x=tBR,y=youtBR[:,2], name='Acc floor 3', mode = 'lines', row=2, col=2)
    # Update xaxis properties
    fig1.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=2, col=2)
    # Update yaxis properties
    fig1.update_yaxes(title_text="dB", titlefont=dict(size=15), row=2, col=2)

    # Update Figure properties
    fig1.update_layout(title_text="<b>--- Experimental Data ---<b>", font=dict(size=20), width=1650, height=600)
    fig1.update_layout(showlegend=True, font=dict(size=15))
    fig1.update_layout(height=800, width=1400)
    fig1.update_layout(title={'y':0.99,'x':0.48,'xanchor': 'center'})
    graph1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('crossvalidation_1.html', plot1=graph1,date=date)



@app.route('/crossval_2')
def Exp_Num_Data():
    """
    This function compares the experimental and numerical data for each prototype
    This does not compare the different prototypes
    """
    # Figure3
    fig3 = make_subplots(rows=2, cols=2,vertical_spacing=0.15,
    subplot_titles=("<b>Prototype 1<b>","<b>Prototype 2<b>", "<b>Prototype 3<b>", "<b>Prototype 4<b>"))

    # Fig3.a
    fig3.add_scatter(x=tSW,y=youtSW[:,0], name='Exp Data', mode = 'lines', row=1, col=1)
    fig3.add_scatter(x=tNumSW,y=youtNumSW[:,0], name='Num Data', mode = 'markers', marker=dict(size= 1.5), row=1, col=1)
    # Update xaxis properties
    fig3.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=1, col=1)
    # Update yaxis properties
    fig3.update_yaxes(title_text="dB", titlefont=dict(size=15),row=1,col=1)

    ## Fig3.b
    fig3.add_scatter(x=tSO,y=youtSO[:,0], name='Exp Data', mode = 'lines', row=1, col=2)
    fig3.add_scatter(x=tNumSO,y=youtNumSO[:,0], name='Num Data', mode = 'markers', marker=dict(size= 1.5), row=1, col=2)
    # Update xaxis properties
    fig3.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=1, col=2)
    # Update yaxis properties
    fig3.update_yaxes(title_text="dB", titlefont=dict(size=15),row=1,col=2)

    #Fig3.c
    fig3.add_scatter(x=tSH,y=youtSH[:,0], name='Exp Data', mode = 'lines', row=2, col=1)
    fig3.add_scatter(x=tNumSH,y=youtNumSH[:,0], name='Num Data', mode = 'markers', marker=dict(size= 1.5), row=2, col=1)
    # Update xaxis properties
    fig3.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=2, col=1)
    # Update yaxis properties
    fig3.update_yaxes(title_text="dB", titlefont=dict(size=15),row=2,col=1)

    #Fig3.d
    fig3.add_scatter(x=tBR,y=youtBR[:,0], name='Exp Data', mode = 'lines', row=2, col=2)
    fig3.add_scatter(x=tNumBR,y=youtNumBR[:,0], name='Num Data', mode = 'markers', marker=dict(size= 3), row=2, col=2)
    # Update xaxis properties
    fig3.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=2, col=2)
    # Update yaxis properties
    fig3.update_yaxes(title_text="dB", titlefont=dict(size=15),row=2,col=2)

    # Update Figure properties
    fig3.update_layout(title_text="<b>--- Experimental vs Numerical Data ---<b>", font=dict(size=20), width=1650, height=600)
    fig3.update_layout(showlegend=True, font=dict(size=15))
    fig3.update_layout(height=800, width=1400)
    fig3.update_layout(title={'y':0.99,'x':0.48,'xanchor': 'center'})

    graph3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('crossvalidation_2.html', plot3=graph3,date=date)



@app.route('/crossval_3')# @app.route('/Num_Data')
def Num_Data():
    """
    This function displays the numerical results for each prototype
    """
    # Figure2
    fig2 = make_subplots(rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.15,
    subplot_titles=("<b>Prototype 1<b>","<b>Prototype 2<b>", "<b>Prototype 3<b>", "<b>Prototype 4<b>"))

    # Fig2.a
    fig2.add_scatter(x=tNumSW,y=youtNumSW[:,0], name='Acc floor 1', mode = 'lines', row=1, col=1)
    fig2.add_scatter(x=tNumSWmiddle,y=youtNumSW[:,1], name='Acc floor 2', mode = 'lines', row=1, col=1)
    fig2.add_scatter(x=tNumSW,y=youtNumSW[:,2], name='Acc floor 3', mode = 'lines', row=1, col=1)
    # Update xaxis properties
    fig2.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=1, col=1)
    # Update yaxis properties
    fig2.update_yaxes(title_text="dB", titlefont=dict(size=15), row=1, col=1)

    ## Fig2.b
    fig2.add_scatter(x=tNumSO,y=youtNumSO[:,0], name='Acc floor 1', mode = 'lines', row=1, col=2)
    fig2.add_scatter(x=tNumSO,y=youtNumSO[:,1], name='Acc floor 2', mode = 'lines', row=1, col=2)
    fig2.add_scatter(x=tNumSO,y=youtNumSO[:,2], name='Acc floor 3', mode = 'lines', row=1, col=2)
    # Update xaxis properties
    fig2.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=1, col=2)
    # Update yaxis properties
    fig2.update_yaxes(title_text="dB", titlefont=dict(size=15), row=1, col=2)

    #Fig2.c
    fig2.add_scatter(x=tNumSH,y=youtNumSH[:,0], name='Acc floor 1', mode = 'lines', row=2, col=1)
    fig2.add_scatter(x=tNumSHmiddle,y=youtNumSH[:,1], name='Acc floor 2', mode = 'lines', row=2, col=1)
    fig2.add_scatter(x=tNumSH,y=youtNumSH[:,2], name='Acc floor 3', mode = 'lines', row=2, col=1)
    # Update xaxis properties
    fig2.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=2, col=1)
    # Update yaxis properties
    fig2.update_yaxes(title_text="dB", titlefont=dict(size=15), row=2, col=1)

    #Fig2.d
    fig2.add_scatter(x=tNumBR,y=youtNumBR[:,0], name='Acc floor 1', mode = 'lines', row=2, col=2)
    fig2.add_scatter(x=tNumBR,y=youtNumBR[:,1], name='Acc floor 2', mode = 'lines', row=2, col=2)
    fig2.add_scatter(x=tNumBR,y=youtNumBR[:,2], name='Acc floor 3', mode = 'lines', row=2, col=2)
    # Update xaxis properties
    fig2.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=15), row=2, col=2)
    # Update yaxis properties
    fig2.update_yaxes(title_text="dB", titlefont=dict(size=15), row=2, col=2)


    # Update Figure properties
    fig2.update_layout(title_text="<b>--- Numerical Data ---<b>", font=dict(size=20), width=1650, height=600)
    fig2.update_layout(showlegend=True, font=dict(size=15))
    fig2.update_layout(height=800, width=1400)
    fig2.update_layout(title={'y':0.99,'x':0.48,'xanchor': 'center'})

    graph2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    
    return render_template('crossvalidation_3.html', plot2=graph2,date=date)


@app.route('/crossval_4') # @app.route('/Exp_Exp_Data')
def Exp_Exp_Data():
    """
    This compares the experimental data across all the prototypes to denote manufacturing/testing variability
    """
    # Figure4
    fig4 = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    fig4.add_scatter(x=tSW,y=youtSW[:,0], name='Prototype 1 - Exp Data', mode = 'lines', row=1, col=1)
    fig4.add_scatter(x=tSO,y=youtSO[:,0], name='Prototype 2 - Exp Data', mode = 'lines', row=1, col=1)
    fig4.add_scatter(x=tSH,y=youtSH[:,0], name='Prototype 3 - Exp Data', mode = 'lines', row=1, col=1)
    fig4.add_scatter(x=tBR,y=youtBR[:,0], name='Prototype 4 - Exp Data', mode = 'lines', row=1, col=1)
    # Update xaxis properties
    fig4.update_xaxes(title_text="Freq (Hz)", titlefont=dict(size=20), row=1, col=1)
    # Update yaxis properties
    fig4.update_yaxes(title_text="dB", titlefont=dict(size=20),row=1,col=1)

        # Update Figure properties
    fig4.update_layout(title_text="<b>--- Experimental vs Experimental Data ---<b>", font=dict(size=20), width=1600, height=800)
    fig4.update_layout(showlegend=True, font=dict(size=15))

    fig4.update_layout(title={'y':0.99,'x':0.48,'xanchor': 'center'})

    graph4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
   
    return render_template('crossvalidation_4.html', plot4=graph4,date=date)

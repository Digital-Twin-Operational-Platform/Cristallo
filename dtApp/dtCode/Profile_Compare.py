from flask import render_template, request, redirect, url_for
import numpy as np, os, csv
from dtApp import app
from dtApp import date
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly
import json

def read_profile_Comp(filename):
    # Read in CSV for model parameters
    A=[]
    try:
        with open(filename,'r', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';',skipinitialspace=True)
            for row in spamreader:
                A.append(row)
        m1,m2,m3=float(A[0][0]),float(A[0][1]),float(A[0][2])
        k1,k2,k3=float(A[1][0]),float(A[1][1]),float(A[1][2])
        c1,c2,c3=float(A[2][0]),float(A[2][1]),float(A[2][2])
        w1,w2,w3=float(A[3][0]),float(A[3][1]),float(A[3][2])
        d1,d2,d3=float(A[4][0]),float(A[4][1]),float(A[4][2])
        m1d1,m1d2,m1d3=float(A[5][0]),float(A[5][1]),float(A[5][2])
        m2d1,m2d2,m2d3=float(A[6][0]),float(A[6][1]),float(A[6][2])
        m3d1,m3d2,m3d3=float(A[7][0]),float(A[7][1]),float(A[7][2])
        
        form={'m1':m1,'m2':m2,'m3':m3,'k1':k1,'k2':k2,'k3':k3,'c1':c1,'c2':c2,
              'c3':c3,'w1':w1,'w2':w2,'w3':w3,'d1':d1,'d2':d2,'d3':d3,'mode1':[0.,m1d1,m1d2,m1d3],
              'mode2':[0.,m2d1,m2d2,m2d3],'mode3':[0.,m3d1,m3d2,m3d3],'name':filename}
    except:
        print("Error in loading CSV File")
        m1,m2,m3=5.0,5.0,5.0
        k1,k2,k3=4000.0,4000.0,4000.0
        c1,c2,c3=2.0,2.0,2.0 
        form={'m1':m1,'m2':m2,'m3':m3,'k1':k1,'k2':k2,'k3':k3,'c1':c1,'c2':c2,
              'c3':c3}
    return(form)
def read_FRF(filename):
    frf = np.genfromtxt(filename, dtype=[complex ,complex,complex,complex], delimiter=';')

    # read data from selected .csv file
    freq = [x[0] for x in frf] # frequency vector [Hz]
    h1 = [x[1] for x in frf] # accelerance sensor 1 [g/N]
    h2 = [x[2] for x in frf] # accelerance sensor 2 [g/N]
    h3 = [x[3] for x in frf] # accelerance sensor 3 [g/N]
    #print(frf)
    #print(h1[0])

    # calculate linear freq and circular freq
    freq = np.real(freq)    # frequency vector [Hz]
    w = 2*np.pi*freq

    # calculate mobility
    y1 = h1/(1j*w)  # mobility position 1
    y2 = h2/(1j*w)  # mobility position 2
    y3 = h3/(1j*w)  # mobility position 3
    
    form={'freq':freq,'F1':y1,'F2':y2,'F3':y3}
    return(form)

@app.route("/Profile_Compare",methods=['GET','POST'])
def Compare_Hub():
    return render_template("Compare_Load.html",date=date)

@app.route("/CompSelect",methods=['GET','POST'])
def DisplayProfiles():
    # Read in Profiles
    # Profile 1
    uploaded_files = request.files["Profile1"]
    filename1 = uploaded_files.filename
    filename='dtApp/dtData/profiles/' + filename1
    form1=read_profile_Comp(filename)
    # Profile 2
    uploaded_files = request.files["Profile2"]
    filename2 = uploaded_files.filename
    filename='dtApp/dtData/profiles/' + filename2
    form2=read_profile_Comp(filename)
    # Profile 3
    uploaded_files = request.files["Profile3"]
    filename3 = uploaded_files.filename
    filename='dtApp/dtData/profiles/' + filename3
    form3=read_profile_Comp(filename)
    # Gather Frequency Domain
    # Profile 1 FRF
    filename='dtApp/dtData/frfs/' + filename1[8:]
    FRF1=read_FRF(filename)
    # Profile 2 FRF
    filename='dtApp/dtData/frfs/' + filename2[8:]
    FRF2=read_FRF(filename)
    # Profile 3 FRF
    filename='dtApp/dtData/frfs/' + filename3[8:]
    FRF3=read_FRF(filename)
    
    # Display FRFs
    fig = make_subplots(rows=1,cols=1,vertical_spacing=0.15)
    fig.add_scatter(x=FRF1['freq'],y=np.abs(FRF1['F3']), name='Profile 1', mode = 'lines', row=1,col=1, line={'color':'black'})
    fig.add_scatter(x=FRF2['freq'],y=np.abs(FRF2['F3']), name='Profile 2', mode = 'lines', row=1,col=1, line={'color':'red'})
    fig.add_scatter(x=FRF3['freq'],y=np.abs(FRF3['F3']), name='Profile 3', mode = 'lines', row=1,col=1, line={'color':'green'})
    fig.update_layout(title_text="<b>--- Frequency Response Functions of 3rd Floor ---<b>", font=dict(size=20), width=1650,height=600)
    fig.update_layout(showlegend=True, font=dict(size=15))
    fig.update_xaxes(range=[2,40])
    fig.update_xaxes(title_text='Frequency [Hz]',titlefont=dict(size=15),row=1,col=1)
    fig.update_yaxes(title_text='Magnitute of Accelerance',type="log",titlefont=dict(size=15),row=1,col=1)
    fig.update_layout(title={'y':0.99,'x':0.48,'xanchor': 'center'})
    graphFRF= json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Display Mode Shapes
    fig1 = make_subplots(rows=1, cols=3,vertical_spacing=0.15, shared_xaxes=True,subplot_titles=("<b>Mode 1<b>","<b>Mode 2<b>", "<b>Mode 3<b>"))
    y=np.array([0,1,2,3])
    # Fig1.a
    fig1.add_scatter(x=-np.array(form1['mode1']),y=y, name='Profile 1', mode = 'lines', row=1, col=1,line={'color':'black','dash':'solid'})
    fig1.add_scatter(x=form2['mode1'],y=y, name='Profile 2', mode = 'lines', row=1, col=1,line={'color':'red','dash':'dashdot'})
    fig1.add_scatter(x=form3['mode1'],y=y, name='Profile 3', mode = 'lines', row=1, col=1,line={'color':'green','dash':'dash'})    
    # Update yaxis properties
    fig1.update_yaxes(title_text="Floor Number", titlefont=dict(size=15), row=1, col=1)

    # Fig1.b
    fig1.add_scatter(x=-np.array(form1['mode2']),y=y, name='', mode = 'lines', row=1, col=2,line={'color':'black','dash':'solid'})
    fig1.add_scatter(x=form2['mode2'],y=y, name='', mode = 'lines', row=1, col=2,line={'color':'red','dash':'dashdot'})
    fig1.add_scatter(x=form3['mode2'],y=y, name='', mode = 'lines', row=1, col=2,line={'color':'green','dash':'dash'})
    # Update xaxis properties
    fig1.update_xaxes(title_text="Normalized Mode Shape", titlefont=dict(size=15), row=1, col=2)

    #Fig1.c
    fig1.add_scatter(x=-np.array(form1['mode3']),y=y, name='', mode = 'lines', row=1, col=3,line={'color':'black','dash':'solid'})
    fig1.add_scatter(x=form2['mode3'],y=y, name='', mode = 'lines', row=1, col=3,line={'color':'red','dash':'dashdot'})
    fig1.add_scatter(x=form3['mode3'],y=y, name='', mode = 'lines', row=1, col=3,line={'color':'green','dash':'dash'})

    # Update Figure properties
    fig1.update_layout(title_text="<b>--- Mode Shape Comparison ---<b>", font=dict(size=20), width=1650, height=600)
    fig1.update_layout(showlegend=True, font=dict(size=15))
    fig1.update_xaxes(range=[-1,1])
    fig1.update_layout(title={'y':0.99,'x':0.48,'xanchor': 'center'})
    # fig1.show(renderer='png')
    graphModes = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    form={'P1Name':filename1,'P2Name':filename2,'P3Name':filename3,
          'P1w1':form1['w1'],'P1w2':form1['w2'],'P1w3':form1['w3'],
          'P1d1':form1['d1'],'P1d2':form1['d2'],'P1d3':form1['d3'],
          'P2w1':form2['w1'],'P2w2':form2['w2'],'P2w3':form2['w3'],
          'P2d1':form2['d1'],'P2d2':form2['d2'],'P2d3':form2['d3'],
          'P3w1':form3['w1'],'P3w2':form3['w2'],'P3w3':form3['w3'],
          'P3d1':form3['d1'],'P3d2':form3['d2'],'P3d3':form3['d3']}
    # return render_template("crossvalidation_4.html", date=date,plot4=graphModes)
    return render_template("ProCompare.html", date=date,form=form, plot1=graphFRF, plot2=graphModes)
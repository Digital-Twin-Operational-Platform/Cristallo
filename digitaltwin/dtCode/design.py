'''
This module contains three app routes:

1: @app.route('/Design_under_uncertainty')
Displays an Input-Data page to define the parameters of the distribution
of the properties of the three-storey building: mass, stiffness, damping
and input force. The parameters of the Gaussian distribution are the
mean value (mu) and standard deviation (sigma), whereas the corresponding
parameters of the Gamma distribution are shape (kappa) and scale (theta)
This page also allows to define the frequency of analysis, the number of
Monte Carlo simulations and the output requested for the Fisher Information
Matrix (the outputs are the displacements of each floor and the shear force
between two floors, at least one output must be selected to proceed)
The default values are given by experimental data gathered at Sheffield University
The Frequency response function displayed is calculated with the mean values.

2: @app.route('/Design_under_uncertainty_output')
Displays the probability distribution of the selected outputs. The number of
bins of the 1-D histogram can be modified. Additionally, it allows to define
the number of bins of the n-dimentional joint pdf of the correlated outputs
for the analysis of the sensitivities based on the Fisher Information Matrix

3: @app.route('/Design_under_uncertainty_fisher')
Plots the scaled form of the Fisher Information Matrix and the corresponding
eigenvalues and eigenvectors

4: @app.route('/Design_under_uncertainty_sensitivity')
Sensitivity analysis given a probability of failure threshold.
'''

from flask import render_template, request, redirect, Response, url_for, send_file, send_from_directory
from io import BytesIO
from numpy import linspace, array, ones, diag, zeros, sqrt, conj, trapz, log10, log, gradient, real
from numpy import arange, hstack, append, histogram, meshgrid, vectorize, where, intersect1d, imag
from numpy.random import normal, gamma
from numpy.linalg import inv
from scipy.linalg import eigh, eig
from scipy.special import digamma
from wtforms import Form, FloatField, validators, SelectField, BooleanField
from math import pi
import io
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
from digitaltwin import date

def dplot4M():

    global m1, m2, m3, k1, k2, k3, c1, c2, c3, f1, f2, f3
    global AllOutput, X_list_all, Y_type, Y_list_all, b_list_all, W, N_realisations
    global m1_mean_o, m2_mean_o, m3_mean_o, m1_sigma_o, m2_sigma_o, m3_sigma_o
    global k1_mean_o, k2_mean_o, k3_mean_o, k1_sigma_o, k2_sigma_o, k3_sigma_o
    global c1_mean_o, c2_mean_o, c3_mean_o, c1_sigma_o, c2_sigma_o, c3_sigma_o
    global f1_mean_o, f2_mean_o, f3_mean_o, f1_sigma_o, f2_sigma_o, f3_sigma_o
    global F1_type_o, F2_type_o, F3_type_o, K1_type_o, K2_type_o, K3_type_o
    global M1_type_o, M2_type_o, M3_type_o, C1_type_o, C2_type_o, C3_type_o
    global freq_analysis_o, n_realisations_o
    global check_x1_o, check_x2_o, check_x3_o, check_s1_o, check_s2_o, check_s3_o

    form = InputForm(request.form)
    if 'y_monteCarlo' not in globals():
        # DEFAULT VALUES (AS GIVEN BY PAUL GARDNER)
        # Type of distribution 1:Gaussian; 2:Gamma
        form.M1_type.data = '1'
        form.M2_type.data = '1'
        form.M3_type.data = '1'

        form.K1_type.data = '1'
        form.K2_type.data = '1'
        form.K3_type.data = '1'

        form.C1_type.data = '1'
        form.C2_type.data = '2'
        form.C3_type.data = '2'

        form.F1_type.data = '1'
        form.F2_type.data = '1'
        form.F3_type.data = '1'

        # Mean or shape depending on the distribution type
        form.f1_mean.data=1.0
        form.f2_mean.data=0
        form.f3_mean.data=0

        form.k1_mean.data=4203.0027
        form.k2_mean.data=4147.6895
        form.k3_mean.data=5101.4822

        form.c1_mean.data=2.2007146
        form.c2_mean.data=0.6018186
        form.c3_mean.data=2.3842358

        form.m1_mean.data=4.8724882
        form.m2_mean.data=5.4758033
        form.m3_mean.data=5.6923249

        # Stanrard deviation or scale depending on the distribution type
        form.f1_sigma.data=0.1
        form.f2_sigma.data=0
        form.f3_sigma.data=0

        form.k1_sigma.data=83.760278
        form.k2_sigma.data=69.627281
        form.k3_sigma.data=56.769849

        form.c1_sigma.data=0.2589255
        form.c2_sigma.data=0.0015333
        form.c3_sigma.data=0.0010963

        form.m1_sigma.data=0.0312982
        form.m2_sigma.data=0.1002168
        form.m3_sigma.data=0.1144056

        form.freq_analysis.data  = 1.97
        form.n_realisations.data = int(1000)

        form.check_x1.data = False
        form.check_x2.data = False
        form.check_x3.data = False
        form.check_s1.data = False
        form.check_s2.data = False
        form.check_s3.data = False

        # define _o data (redundant if 'Enter input data' has been submited )
        F1_type_o = form.F1_type.data
        F2_type_o = form.F2_type.data
        F3_type_o = form.F3_type.data

        K1_type_o = form.K1_type.data
        K2_type_o = form.K2_type.data
        K3_type_o = form.K3_type.data

        C1_type_o = form.C1_type.data
        C2_type_o = form.C2_type.data
        C3_type_o = form.C3_type.data

        M1_type_o = form.M1_type.data
        M2_type_o = form.M2_type.data
        M3_type_o = form.M3_type.data

        f1_mean_o = form.f1_mean.data
        f2_mean_o = form.f2_mean.data
        f3_mean_o = form.f3_mean.data

        k1_mean_o = form.k1_mean.data
        k2_mean_o = form.k2_mean.data
        k3_mean_o = form.k3_mean.data

        c1_mean_o = form.c1_mean.data
        c2_mean_o = form.c2_mean.data
        c3_mean_o = form.c3_mean.data

        m1_mean_o = form.m1_mean.data
        m2_mean_o = form.m2_mean.data
        m3_mean_o = form.m3_mean.data

        f1_sigma_o = form.f1_sigma.data
        f2_sigma_o = form.f2_sigma.data
        f3_sigma_o = form.f3_sigma.data

        k1_sigma_o = form.k1_sigma.data
        k2_sigma_o = form.k2_sigma.data
        k3_sigma_o = form.k3_sigma.data

        c1_sigma_o = form.c1_sigma.data
        c2_sigma_o = form.c2_sigma.data
        c3_sigma_o = form.c3_sigma.data

        m1_sigma_o = form.m1_sigma.data
        m2_sigma_o = form.m2_sigma.data
        m3_sigma_o = form.m3_sigma.data

        freq_analysis_o  = form.freq_analysis.data
        n_realisations_o = int(form.n_realisations.data)

        check_x1_o = form.check_x1.data
        check_x2_o = form.check_x2.data
        check_x3_o = form.check_x3.data
        check_s1_o = form.check_s1.data
        check_s2_o = form.check_s2.data
        check_s3_o = form.check_s3.data


    else:
        if form.m1_mean.data is not None:

            F1_type_o = form.F1_type.data
            F2_type_o = form.F2_type.data
            F3_type_o = form.F3_type.data

            K1_type_o = form.K1_type.data
            K2_type_o = form.K2_type.data
            K3_type_o = form.K3_type.data

            C1_type_o = form.C1_type.data
            C2_type_o = form.C2_type.data
            C3_type_o = form.C3_type.data

            M1_type_o = form.M1_type.data
            M2_type_o = form.M2_type.data
            M3_type_o = form.M3_type.data


            f1_mean_o = form.f1_mean.data
            f2_mean_o = form.f2_mean.data
            f3_mean_o = form.f3_mean.data

            k1_mean_o = form.k1_mean.data
            k2_mean_o = form.k2_mean.data
            k3_mean_o = form.k3_mean.data

            c1_mean_o = form.c1_mean.data
            c2_mean_o = form.c2_mean.data
            c3_mean_o = form.c3_mean.data

            m1_mean_o = form.m1_mean.data
            m2_mean_o = form.m2_mean.data
            m3_mean_o = form.m3_mean.data

            f1_sigma_o = form.f1_sigma.data
            f2_sigma_o = form.f2_sigma.data
            f3_sigma_o = form.f3_sigma.data

            k1_sigma_o = form.k1_sigma.data
            k2_sigma_o = form.k2_sigma.data
            k3_sigma_o = form.k3_sigma.data

            c1_sigma_o = form.c1_sigma.data
            c2_sigma_o = form.c2_sigma.data
            c3_sigma_o = form.c3_sigma.data

            m1_sigma_o = form.m1_sigma.data
            m2_sigma_o = form.m2_sigma.data
            m3_sigma_o = form.m3_sigma.data

            freq_analysis_o  = form.freq_analysis.data
            n_realisations_o = int(form.n_realisations.data)

            check_x1_o = form.check_x1.data
            check_x2_o = form.check_x2.data
            check_x3_o = form.check_x3.data
            check_s1_o = form.check_s1.data
            check_s2_o = form.check_s2.data
            check_s3_o = form.check_s3.data

        else:

            form.F1_type.data = F1_type_o
            form.F2_type.data = F2_type_o
            form.F3_type.data = F3_type_o

            form.K1_type.data = K1_type_o
            form.K2_type.data = K2_type_o
            form.K3_type.data = K3_type_o

            form.C1_type.data = C1_type_o
            form.C2_type.data = C2_type_o
            form.C3_type.data = C3_type_o

            form.M1_type.data = M1_type_o
            form.M2_type.data = M2_type_o
            form.M3_type.data = M3_type_o

            form.f1_mean.data = f1_mean_o
            form.f2_mean.data = f2_mean_o
            form.f3_mean.data = f3_mean_o

            form.k1_mean.data = k1_mean_o
            form.k2_mean.data = k2_mean_o
            form.k3_mean.data = k3_mean_o

            form.c1_mean.data = c1_mean_o
            form.c2_mean.data = c2_mean_o
            form.c3_mean.data = c3_mean_o

            form.m1_mean.data = m1_mean_o
            form.m2_mean.data = m2_mean_o
            form.m3_mean.data = m3_mean_o

            form.f1_sigma.data = f1_sigma_o
            form.f2_sigma.data = f2_sigma_o
            form.f3_sigma.data = f3_sigma_o

            form.k1_sigma.data = k1_sigma_o
            form.k2_sigma.data = k2_sigma_o
            form.k3_sigma.data = k3_sigma_o

            form.c1_sigma.data = c1_sigma_o
            form.c2_sigma.data = c2_sigma_o
            form.c3_sigma.data = c3_sigma_o

            form.m1_sigma.data = m1_sigma_o
            form.m2_sigma.data = m2_sigma_o
            form.m3_sigma.data = m3_sigma_o

            form.freq_analysis.data  = freq_analysis_o
            form.n_realisations.data = n_realisations_o

            form.check_x1.data = check_x1_o
            form.check_x2.data = check_x2_o
            form.check_x3.data = check_x3_o
            form.check_s1.data = check_s1_o
            form.check_s2.data = check_s2_o
            form.check_s3.data = check_s3_o

    # Define the mean values for the nominal FRF

    if int(form.M1_type.data)==1:
        m1 = form.m1_mean.data
    elif int(form.M1_type.data)==2:
        m1 = form.m1_mean.data*form.m1_sigma.data

    if int(form.M2_type.data)==1:
        m2 = form.m2_mean.data
    elif int(form.M2_type.data)==2:
        m2 = form.m2_mean.data*form.m2_sigma.data

    if int(form.M3_type.data)==1:
        m3 = form.m3_mean.data
    elif int(form.M3_type.data)==2:
        m3 = form.m3_mean.data*form.m3_sigma.data


    if int(form.K1_type.data)==1:
        k1 = form.k1_mean.data
    elif int(form.K1_type.data)==2:
        k1 = form.k1_mean.data*form.k1_sigma.data

    if int(form.K2_type.data)==1:
        k2 = form.k2_mean.data
    elif int(form.K2_type.data)==2:
        k2 = form.k2_mean.data*form.k2_sigma.data

    if int(form.K3_type.data)==1:
        k3 = form.k3_mean.data
    elif int(form.K3_type.data)==2:
        k3 = form.k3_mean.data*form.k3_sigma.data


    if int(form.C1_type.data)==1:
        c1 = form.c1_mean.data
    elif int(form.C1_type.data)==2:
        c1 = form.c1_mean.data*form.c1_sigma.data

    if int(form.C2_type.data)==1:
        c2 = form.c2_mean.data
    elif int(form.C2_type.data)==2:
        c2 = form.c2_mean.data*form.c2_sigma.data

    if int(form.C3_type.data)==1:
        c3 = form.c3_mean.data
    elif int(form.C3_type.data)==2:
        c3 = form.c3_mean.data*form.c3_sigma.data


    if int(form.F1_type.data)==1:
        f1 = form.f1_mean.data
    elif int(form.F1_type.data)==2:
        f1 = form.f1_mean.data*form.f1_sigma.data

    if int(form.F2_type.data)==1:
        f2 = form.f2_mean.data
    elif int(form.F2_type.data)==2:
        f2 = form.f2_mean.data*form.f2_sigma.data

    if int(form.F3_type.data)==1:
        f3 = form.f3_mean.data
    elif int(form.F3_type.data)==2:
        f3 = form.f3_mean.data*form.f3_sigma.data

    # Stiffness, Damping and Mass matrices

    K = array([[k1+k2 ,-k2    , 0  ],
               [-k2   , k2+k3 , -k3],
               [ 0    ,-k3    , k3 ]])

    C = array([[c1+c2 ,-c2    , 0  ],
               [-c2   , c2+c3 , -c3],
               [ 0    ,-c3    , c3 ]])

    M = array([[m1    ,0      ,0  ],
               [0     ,m2     ,0  ],
               [0     ,0      ,m3 ]])

    # compute eigenvalues and vecors
    eigvals, eigvecs = eigh(K,M)
    fn    = sqrt(eigvals)/(2*pi) # natural frequencies in Hertz
    freq1 = fn[0]
    freq2 = fn[1]
    freq3 = fn[2]

    # Compute FRF including damping
    Md = diag(ones(6),0)
    Md[3:,3: ] = M

    D = 1*diag(-1*ones(3),3)
    D[3:,0:3] = K
    D[3:,3: ] = C

    def responseX_damped(omega,force1,force2,force3):
        f_vector = array([[0],[0],[0],[force1],[force2],[force3]])
        Y_vector = inv(D+(1j*Md*omega))@f_vector
        X_vector = sqrt(Y_vector*conj(Y_vector))
        return (X_vector[0][0], X_vector[1][0], X_vector[2][0],
                X_vector[3][0], X_vector[4][0], X_vector[5][0])

    Omega = 2*pi*linspace(0,1.5*freq3,10000)

    X = vectorize(responseX_damped)(Omega,f1,f2,f3)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05)
    fig.update_layout(title_text="Displacement Frequency Response Function",
                      font=dict(family='Arial, monospace', size=18, color='blue'),
                      width=600, height=685,title_x=0.5,plot_bgcolor= 'rgba(0, 0, 0, 0)'
                      ,paper_bgcolor= 'rgba(0, 0, 0, 0)')
    floorname=['1st floor','2nd floor','3rd floor']
    for i in [0,1,2]:
        fig.add_scatter(x=Omega/(2*pi),y=20*log10(abs(X[i])), name=floorname[i],
                        mode = 'lines', row=int(i+1), col=1)
        fig.update_yaxes(title_text='dB', titlefont=dict(size=15), row=int(i+1), col=1)

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black',
                     zeroline=True,showgrid=True, gridwidth=0.5, gridcolor='Grey',
                     zerolinewidth=0.5, zerolinecolor='Grey')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black',
                     zeroline=True,showgrid=True, gridwidth=0.5, gridcolor='Grey',
                     zerolinewidth=0.5, zerolinecolor='Grey')
    fig.update_xaxes(title_text='Frequency [Hz]', titlefont=dict(size=15), row=3, col=1)
    fig.update_layout(showlegend=True, font=dict(size=15))

    graphJSONfrf = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # request outputs (True/False)
    AllOutput = [form.check_x1.data,
                 form.check_x2.data,
                 form.check_x3.data,
                 form.check_s1.data,
                 form.check_s2.data,
                 form.check_s3.data]

    N_realisations  =  int(form.n_realisations.data)
    W = 2*pi*form.freq_analysis.data

    X_list_all = ['displacement x1 [m]','displacement x2 [m]','displacement x3 [m]',
                  'shear force s1 [N]' ,'shear force s2 [N]' ,'shear force s3 [N]']

    Y_type = [form.F1_type.data, form.F2_type.data, form.F3_type.data,
              form.K1_type.data, form.K2_type.data, form.K3_type.data,
              form.C1_type.data, form.C2_type.data, form.C3_type.data,
              form.M1_type.data, form.M2_type.data, form.M3_type.data]

    Y_list_all = ['mean f1','mean f2','mean f3',
                  'mean k1','mean k2','mean k3',
                  'mean c1','shape c2','shape c3',
                  'mean m1','mean m2','mean m3',
                  'sigma f1','sigma f2','sigma f3',
                  'sigma k1','sigma k2','sigma k3',
                  'sigma c1','scale c2','scale c3',
                  'sigma m1','sigma m2','sigma m3']

    b_list_all = array([form.f1_mean.data,form.f2_mean.data,form.f3_mean.data,
                        form.k1_mean.data,form.k2_mean.data,form.k3_mean.data,
                        form.c1_mean.data,form.c2_mean.data,form.c3_mean.data,
                        form.m1_mean.data,form.m2_mean.data,form.m3_mean.data,
                        form.f1_sigma.data,form.f2_sigma.data,form.f3_sigma.data,
                        form.k1_sigma.data,form.k2_sigma.data,form.k3_sigma.data,
                        form.c1_sigma.data,form.c2_sigma.data,form.c3_sigma.data,
                        form.m1_sigma.data,form.m2_sigma.data,form.m3_sigma.data])

    global x_outputs_list,y_inputs_list
    global valid_b_half   # logic values of deterministic and statistic half
    global valid_b_all    # logic values of deterministic and statistic doubled
    global b_list         # array of valid b (mean and sigma)
    global Y_list         # names of valid inputs
    global y_mean_list    # position of valid b mean
    global y_sigma_list   # position of valid b sigma
    global x_monteCarlo   # outputs
    global y_monteCarlo
    global X_outputs_all


    def responseX_damped_Random(omega,F1,F2,F3,K1,K2,K3,C1,C2,C3,M1,M2,M3):

        K = array([[K1+K2,-K2,0],[-K2,K2+K3,-K3],[0,-K3,K3]])
        C = array([[C1+C2,-C2,0],[-C2,C2+C3,-C3],[0,-C3,C3]])
        M = array([[M1,0,0],[0,M2,0],[0,0,M3]])

        Md = diag(ones(6),0)
        Md[3:,3: ] = M

        D = 1*diag(-1*ones(3),3)
        D[3:,0:3] = K
        D[3:,3: ] = C

        f_vector = array([[0],[0],[0],[F1],[F2],[F3]])
        Y_vector = inv(D+(1j*Md*omega))@f_vector
        X_vector = abs(sqrt(Y_vector*conj(Y_vector)))
        return (X_vector[0][0], X_vector[1][0], X_vector[2][0],
                X_vector[3][0], X_vector[4][0], X_vector[5][0])

# MONTE CARLO SIMULATIONS

# variables without standard deviation are deterministic
    valid_b_half = b_list_all[int(len(Y_list_all)/2):]!=0
    valid_b_all  = hstack((valid_b_half,valid_b_half))

    b_list = b_list_all[valid_b_all]
    Y_list = []
    for i in arange(len(Y_list_all)):
        if valid_b_all[i]:
            Y_list.append(Y_list_all[i])

    y_mean_list = []
    y_sigma_list= []
    for i in arange(int(len(Y_list_all)/2)):
        if b_list_all[int(len(Y_list_all)/2):][i]!=0:
            y_mean_list.append(i)
            y_sigma_list.append(int((len(Y_list_all)/2)+i))



    if 'flag_2' in globals():
        pass
    else:

        y_monteCarlo = {}
        for i in arange(int(len(Y_list_all)/2)):
            if Y_type[i]=='1':
                y_monteCarlo[i]=normal(b_list_all[i],b_list_all[int((len(Y_list_all)/2)+i)], N_realisations)
            elif Y_type[i]=='2':
                y_monteCarlo[i]=gamma(b_list_all[i],(b_list_all[int((len(Y_list_all)/2)+i)]), N_realisations)

        OutX = vectorize(responseX_damped_Random)(W,y_monteCarlo[0],
                                                    y_monteCarlo[1],
                                                    y_monteCarlo[2],
                                                    y_monteCarlo[3],
                                                    y_monteCarlo[4],
                                                    y_monteCarlo[5],
                                                    y_monteCarlo[6],
                                                    y_monteCarlo[7],
                                                    y_monteCarlo[8],
                                                    y_monteCarlo[9],
                                                    y_monteCarlo[10],
                                                    y_monteCarlo[11])

        x1, x2, x3 = [OutX[0],OutX[1],OutX[2]]

        # Shear force
        s1 = y_monteCarlo[3]*x1
        s2 = y_monteCarlo[4]*(x2-x1)
        s3 = y_monteCarlo[5]*(x3-x2)

        X_outputs_all = {0:x1,1:x2,2:x3,3:s1,4:s2,5:s3}
        x_monteCarlo  = {}
        for i in arange(int(len(AllOutput))):
            if AllOutput[i] is True:
                x_monteCarlo[i]=X_outputs_all[i]
        y_inputs_list = list(y_monteCarlo.keys())
        x_outputs_list = list(x_monteCarlo.keys())

    if 'flag_2' in globals():
        del globals()['flag_2']
    if 'Fjk_IMP_normalised' in globals():
        del globals()['Fjk_IMP_normalised']


    return render_template('design.html', form=form, plot=graphJSONfrf,date=date)


class InputForm(Form):

    M1_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    M2_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    M3_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])

    K1_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    K2_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    K3_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])

    C1_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    C2_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    C3_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])

    F1_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    F2_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])
    F3_type = SelectField(label='Type',validators=[validators.InputRequired()],choices=[(1, 'Gaussian'), (2, 'Gamma')])

    # mean or shape, depending on the distribution type
    f1_mean=FloatField(label='f1 mean', validators=[validators.InputRequired()])
    f2_mean=FloatField(label='f2 mean', validators=[validators.InputRequired()])
    f3_mean=FloatField(label='f3 mean', validators=[validators.InputRequired()])

    k1_mean=FloatField(label='k1 mean', validators=[validators.InputRequired()])
    k2_mean=FloatField(label='k2 mean', validators=[validators.InputRequired()])
    k3_mean=FloatField(label='k3 mean', validators=[validators.InputRequired()])

    c1_mean=FloatField(label='c1 mean', validators=[validators.InputRequired()])
    c2_mean=FloatField(label='c2 mean', validators=[validators.InputRequired()])
    c3_mean=FloatField(label='c3 mean', validators=[validators.InputRequired()])

    m1_mean=FloatField(label='m1 mean', validators=[validators.InputRequired()])
    m2_mean=FloatField(label='m2 mean', validators=[validators.InputRequired()])
    m3_mean=FloatField(label='m3 mean', validators=[validators.InputRequired()])

    # Stanrard deviation or scale depending on the distribution type
    f1_sigma=FloatField(label='f1 sigma', validators=[validators.InputRequired()])
    f2_sigma=FloatField(label='f2 sigma', validators=[validators.InputRequired()])
    f3_sigma=FloatField(label='f3 sigma', validators=[validators.InputRequired()])

    k1_sigma=FloatField(label='k1 sigma', validators=[validators.InputRequired()])
    k2_sigma=FloatField(label='k2 sigma', validators=[validators.InputRequired()])
    k3_sigma=FloatField(label='k3 sigma', validators=[validators.InputRequired()])

    c1_sigma=FloatField(label='c1 sigma', validators=[validators.InputRequired()])
    c2_sigma=FloatField(label='c2 sigma', validators=[validators.InputRequired()])
    c3_sigma=FloatField(label='c3 sigma', validators=[validators.InputRequired()])

    # m1_sigma=FloatField(label='m1 sigma', default=0.0312982, validators=[validators.InputRequired()])
    m1_sigma=FloatField(label='m1 sigma', validators=[validators.InputRequired()])
    m2_sigma=FloatField(label='m2 sigma', validators=[validators.InputRequired()])
    m3_sigma=FloatField(label='m3 sigma', validators=[validators.InputRequired()])

    Xsize=FloatField(label='x_size', default=20, validators=[validators.InputRequired()])
    JPDFsize=FloatField(label='jpdf_size', validators=[validators.InputRequired()])

    # Frequency of analysis
    freq_analysis=FloatField(label='Frequency of Analysis', validators=[validators.InputRequired()])
    # Numer of Monte Carlo realisations
    n_realisations=FloatField(label='N Monte Carlo', validators=[validators.InputRequired()])

    #requested outputs
    check_x1=BooleanField(label='Displacement x1')
    check_x2=BooleanField(label='Displacement x2')
    check_x3=BooleanField(label='Displacement x3')
    check_s1=BooleanField(label='Shear force s1')
    check_s2=BooleanField(label='Shear force s2')
    check_s3=BooleanField(label='Shear force s3')

def OutDis():
    global flag_2
    global global_xMIN, global_xMAX
    flag_2 = 'Output_distribution'

    form = InputForm(request.form)
    global_xMIN = {}
    global_xMAX = {}
    for i in x_outputs_list:
        global_xMIN[i]=min(x_monteCarlo[i])
        global_xMAX[i]=max(x_monteCarlo[i])

    graphJSONhist = json.dumps(Histo(x_outputs_list,int(form.Xsize.data)), cls=plotly.utils.PlotlyJSONEncoder)


    if request.method=='POST':
        for key,val in request.form.items():

            if key == "0":
                pass
            elif key == "1":
                graphJSONhist = json.dumps(Histo([0],int(form.Xsize.data)), cls=plotly.utils.PlotlyJSONEncoder)
            elif key == "2":
                graphJSONhist = json.dumps(Histo([1],int(form.Xsize.data)), cls=plotly.utils.PlotlyJSONEncoder)
            elif key == "3":
                graphJSONhist = json.dumps(Histo([2],int(form.Xsize.data)), cls=plotly.utils.PlotlyJSONEncoder)
            elif key == "4":
                graphJSONhist = json.dumps(Histo([3],int(form.Xsize.data)), cls=plotly.utils.PlotlyJSONEncoder)
            elif key == "5":
                graphJSONhist = json.dumps(Histo([4],int(form.Xsize.data)), cls=plotly.utils.PlotlyJSONEncoder)
            elif key == "6":
                graphJSONhist = json.dumps(Histo([5],int(form.Xsize.data)), cls=plotly.utils.PlotlyJSONEncoder)

    # keep working
    global JPDFsize_o
    if 'Fjk_IMP_normalised' not in globals():
        if 'JPDFsize_o' not in globals():
            form.JPDFsize.data = int(10)
            # define _o data (redundant if 'Enter input data' has been submited )
            JPDFsize_o = int(form.JPDFsize.data)
        else:
            if form.JPDFsize.data is not None:
                JPDFsize_o = int(form.JPDFsize.data)
            else:
                form.JPDFsize.data = JPDFsize_o
    else:
        if form.JPDFsize.data is not None:
            JPDFsize_o = int(form.JPDFsize.data)
        else:
            form.JPDFsize.data = JPDFsize_o

    if 'Fjk_IMP_normalised' in globals():
        del globals()['Fjk_IMP_normalised']
    if 'num' in globals():
        del globals()['num']

    return render_template('design_output.html', form=form, plot=graphJSONhist,date=date)

def Histo(I,N_bins):

    Width_o  = 400
    Height_o = 450

    if len(I) ==0:
        Grid = (1 , 1)
        Dim  = (Width_o, Height_o)
        fig = make_subplots(rows=1, cols=1, shared_xaxes=False, vertical_spacing=0.1)


    if len(I) in range(1,4):
        Grid = (1 , len(I))
        Dim  = (Width_o*len(I), Height_o)
    elif len(I) == 4:
        Grid = (2,2)
        Dim  = (2*Width_o, 2*Height_o)
    elif len(I) in range(5,7):
        Grid = (2,3)
        Dim  = (3*Width_o, 2*Height_o)

    fig = make_subplots(rows=Grid[0], cols=Grid[1], shared_xaxes=False, vertical_spacing=0.1)
    fig.update_layout(width=Dim[0], height=Dim[1])

    for i in arange(len(I)):

        if len(I) in [1,2,3, 5,6]:
            if i in range(0,3):
                Pos_Grid = (1,int(i+1))
            else:
                Pos_Grid = (2,int(i-2))

        elif len(I) == 4:
            if i in range(0,2):
                Pos_Grid = (1,int(i+1))
            else:
                Pos_Grid = (2,int(i-1))

        counts, bins = histogram(X_outputs_all[I[i]], bins=N_bins, range=None, density=True)
        bins = 0.5 * (bins[:-1] + bins[1:])
        fig.add_bar(x=bins,y=counts, name='histogram', row=Pos_Grid[0], col=Pos_Grid[1])
        fig.add_scatter(x=bins,y=counts, name='pdf', mode = 'lines', row=Pos_Grid[0], col=Pos_Grid[1])
        fig.update_xaxes(title_text=X_list_all[I[i]], titlefont=dict(size=15), row=Pos_Grid[0], col=Pos_Grid[1])

    fig.update_layout(title_text="1-D histograms and PDF's of the outputs",
                      font=dict(family='Arial, monospace', size=18, color='blue'),
                      title_x=0.5,plot_bgcolor= 'rgba(0, 0, 0, 0)',
                      paper_bgcolor= 'rgba(0, 0, 0, 0)')
    fig.update_xaxes(showgrid=False, gridwidth=0.5, gridcolor='Grey',
                     zeroline=False, zerolinewidth=0.5, zerolinecolor='Grey',
                     showline=True, linewidth=1, linecolor='black')

    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='Grey',
                     zeroline=False, zerolinewidth=0.5, zerolinecolor='Grey',
                     showline=True, linewidth=1, linecolor='black')
    fig.update_layout(showlegend=False, font=dict(size=15))

    return fig


def start_method():
    from functools import reduce
    global x_target, X_target_GRID , px_correlated , PF_correlated ,S_pK,s_pk
    global Gx , Gy, Fjk_IMP_normalised, Y_listtext, lamIMnorm , vIMnorm, num, values_eig, vIM
    global JPDFsize

    form = InputForm(request.form)

    if 'Fjk_IMP_normalised' in globals():
        pass
    else:
        JPDFsize = int(JPDFsize_o)

        x_target = {}
        for i in x_outputs_list:
            x_target[i] = linspace(global_xMIN[i],global_xMAX[i],int(JPDFsize))


        X_target_GRID = {}

        if len(x_outputs_list)==1:
            X_target_GRID[x_outputs_list[0]] = x_target[x_outputs_list[0]]
        elif len(x_outputs_list)==2:
            X_target_GRID[x_outputs_list[0]],X_target_GRID[x_outputs_list[1]] = meshgrid(x_target[x_outputs_list[0]],
                                                                                         x_target[x_outputs_list[1]])
        elif len(x_outputs_list)==3:
            X_target_GRID[x_outputs_list[0]],X_target_GRID[x_outputs_list[1]],X_target_GRID[x_outputs_list[2]]= meshgrid(x_target[x_outputs_list[0]],
                                                                                                                         x_target[x_outputs_list[1]],
                                                                                                                         x_target[x_outputs_list[2]])
        elif len(x_outputs_list)==4:
            X_target_GRID[x_outputs_list[0]],X_target_GRID[x_outputs_list[1]],X_target_GRID[x_outputs_list[2]],X_target_GRID[x_outputs_list[3]]= meshgrid(x_target[x_outputs_list[0]],
                                                                                                                                                          x_target[x_outputs_list[1]],
                                                                                                                                                          x_target[x_outputs_list[2]],
                                                                                                                                                          x_target[x_outputs_list[3]])
        elif len(x_outputs_list)==5:
            X_target_GRID[x_outputs_list[0]],X_target_GRID[x_outputs_list[1]],X_target_GRID[x_outputs_list[2]],X_target_GRID[x_outputs_list[3]],X_target_GRID[x_outputs_list[4]]= meshgrid(x_target[x_outputs_list[0]],
                                                                                                                                                                                           x_target[x_outputs_list[1]],
                                                                                                                                                                                           x_target[x_outputs_list[2]],
                                                                                                                                                                                           x_target[x_outputs_list[3]],
                                                                                                                                                                                           x_target[x_outputs_list[4]])
        elif len(x_outputs_list)==6:
            X_target_GRID[x_outputs_list[0]],X_target_GRID[x_outputs_list[1]],X_target_GRID[x_outputs_list[2]],X_target_GRID[x_outputs_list[3]],X_target_GRID[x_outputs_list[4]],X_target_GRID[x_outputs_list[5]]= meshgrid(x_target[x_outputs_list[0]],
                                                                                                                                                                                                                            x_target[x_outputs_list[1]],                                                                                                                                                                                                   x_target[x_outputs_list[5]])

    #COMPUTE CDF and CDF SENSITIVITIES

        PF_correlated   = zeros(X_target_GRID[x_outputs_list[0]].shape)

        S_pK = {}
        for i in hstack((y_mean_list,y_sigma_list)):
            S_pK[i] = zeros(X_target_GRID[x_outputs_list[0]].shape)

        if len(x_outputs_list)==1:
            for i in arange(PF_correlated.shape[0]):
                intersect_pos = (where((x_monteCarlo[x_outputs_list[0]]<X_target_GRID[x_outputs_list[0]][i])==True))[0]
                PF_correlated[i]   = len(intersect_pos)/N_realisations
                for z in arange(len(y_mean_list)):
                    if Y_type[y_mean_list[z]] == '1':
                        S_pK[y_mean_list[z]][i]  = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])/(b_list_all[y_sigma_list[z]]**2))/N_realisations
                        S_pK[y_sigma_list[z]][i] = sum(((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])**2 - b_list_all[y_sigma_list[z]]**2)/(b_list_all[y_sigma_list[z]]**3))/N_realisations
                    elif Y_type[y_mean_list[z]] == '2':
                        S_pK[y_mean_list[z]][i]  = sum(log(y_monteCarlo[y_mean_list[z]][intersect_pos]/b_list_all[y_sigma_list[z]])-digamma(b_list_all[y_mean_list[z]]))/N_realisations ##########
                        S_pK[y_sigma_list[z]][i] = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]/(b_list_all[y_sigma_list[z]]**2)) - (b_list_all[y_mean_list[z]]/b_list_all[y_sigma_list[z]]))/N_realisations


        elif len(x_outputs_list)==2:
            for i in arange(PF_correlated.shape[0]):
                for j in arange(PF_correlated.shape[1]):

                    intersect_pos = reduce(intersect1d,((where((x_monteCarlo[x_outputs_list[0]]<X_target_GRID[x_outputs_list[0]][i,j])==True))[0],
                                                (where((x_monteCarlo[x_outputs_list[1]]<X_target_GRID[x_outputs_list[1]][i,j])==True))[0]))
                    PF_correlated[i,j]   = len(intersect_pos)/N_realisations
                    for z in arange(len(y_mean_list)):
                        if Y_type[y_mean_list[z]] == '1':
                            S_pK[y_mean_list[z]][i,j]  = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])/(b_list_all[y_sigma_list[z]]**2))/N_realisations
                            S_pK[y_sigma_list[z]][i,j] = sum(((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])**2 - b_list_all[y_sigma_list[z]]**2)/(b_list_all[y_sigma_list[z]]**3))/N_realisations
                        elif Y_type[y_mean_list[z]] == '2':
                            S_pK[y_mean_list[z]][i,j]  = sum(log(y_monteCarlo[y_mean_list[z]][intersect_pos]/b_list_all[y_sigma_list[z]])-digamma(b_list_all[y_mean_list[z]]))/N_realisations
                            S_pK[y_sigma_list[z]][i,j] = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]/(b_list_all[y_sigma_list[z]]**2)) - (b_list_all[y_mean_list[z]]/b_list_all[y_sigma_list[z]]))/N_realisations


        elif len(x_outputs_list)==3:
            for i in arange(PF_correlated.shape[0]):
                for j in arange(PF_correlated.shape[1]):
                    for k in arange(PF_correlated.shape[2]):
                        intersect_pos = reduce(intersect1d,((where((x_monteCarlo[x_outputs_list[0]]<X_target_GRID[x_outputs_list[0]][i,j,k])==True))[0],
                                                            (where((x_monteCarlo[x_outputs_list[1]]<X_target_GRID[x_outputs_list[1]][i,j,k])==True))[0],
                                                            (where((x_monteCarlo[x_outputs_list[2]]<X_target_GRID[x_outputs_list[2]][i,j,k])==True))[0]))
                        PF_correlated[i,j,k]   = len(intersect_pos)/N_realisations
                        for z in arange(len(y_mean_list)):
                            if Y_type[y_mean_list[z]] == '1':
                                S_pK[y_mean_list[z]][i,j,k]  = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])/(b_list_all[y_sigma_list[z]]**2))/N_realisations
                                S_pK[y_sigma_list[z]][i,j,k] = sum(((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])**2 - b_list_all[y_sigma_list[z]]**2)/(b_list_all[y_sigma_list[z]]**3))/N_realisations
                            elif Y_type[y_mean_list[z]] == '2':
                                S_pK[y_mean_list[z]][i,j,k]  = sum(log(y_monteCarlo[y_mean_list[z]][intersect_pos]/b_list_all[y_sigma_list[z]])-digamma(b_list_all[y_mean_list[z]]))/N_realisations
                                S_pK[y_sigma_list[z]][i,j,k] = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]/(b_list_all[y_sigma_list[z]]**2)) - (b_list_all[y_mean_list[z]]/b_list_all[y_sigma_list[z]]))/N_realisations


        elif len(x_outputs_list)==4:
            for i in arange(PF_correlated.shape[0]):
                for j in arange(PF_correlated.shape[1]):
                    for k in arange(PF_correlated.shape[2]):
                        for l in arange(PF_correlated.shape[3]):
                            intersect_pos = reduce(intersect1d,((where((x_monteCarlo[x_outputs_list[0]]<X_target_GRID[x_outputs_list[0]][i,j,k,l])==True))[0],
                                                                (where((x_monteCarlo[x_outputs_list[1]]<X_target_GRID[x_outputs_list[1]][i,j,k,l])==True))[0],
                                                                (where((x_monteCarlo[x_outputs_list[2]]<X_target_GRID[x_outputs_list[2]][i,j,k,l])==True))[0],
                                                                (where((x_monteCarlo[x_outputs_list[3]]<X_target_GRID[x_outputs_list[3]][i,j,k,l])==True))[0]))
                            PF_correlated[i,j,k,l]   = len(intersect_pos)/N_realisations
                            for z in arange(len(y_mean_list)):
                                if Y_type[y_mean_list[z]] == '1':
                                    S_pK[y_mean_list[z]][i,j,k,l]  = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])/(b_list_all[y_sigma_list[z]]**2))/N_realisations
                                    S_pK[y_sigma_list[z]][i,j,k,l] = sum(((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])**2 - b_list_all[y_sigma_list[z]]**2)/(b_list_all[y_sigma_list[z]]**3))/N_realisations
                                elif Y_type[y_mean_list[z]] == '2':
                                    S_pK[y_mean_list[z]][i,j,k,l]  = sum(log(y_monteCarlo[y_mean_list[z]][intersect_pos]/b_list_all[y_sigma_list[z]])-digamma(b_list_all[y_mean_list[z]]))/N_realisations
                                    S_pK[y_sigma_list[z]][i,j,k,l] = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]/(b_list_all[y_sigma_list[z]]**2)) - (b_list_all[y_mean_list[z]]/b_list_all[y_sigma_list[z]]))/N_realisations


        elif len(x_outputs_list)==5:
            for i in arange(PF_correlated.shape[0]):
                for j in arange(PF_correlated.shape[1]):
                    for k in arange(PF_correlated.shape[2]):
                        for l in arange(PF_correlated.shape[3]):
                            for m in arange(PF_correlated.shape[4]):
                                intersect_pos = reduce(intersect1d,((where((x_monteCarlo[x_outputs_list[0]]<X_target_GRID[x_outputs_list[0]][i,j,k,l,m])==True))[0],
                                                                    (where((x_monteCarlo[x_outputs_list[1]]<X_target_GRID[x_outputs_list[1]][i,j,k,l,m])==True))[0],
                                                                    (where((x_monteCarlo[x_outputs_list[2]]<X_target_GRID[x_outputs_list[2]][i,j,k,l,m])==True))[0],
                                                                    (where((x_monteCarlo[x_outputs_list[3]]<X_target_GRID[x_outputs_list[3]][i,j,k,l,m])==True))[0],
                                                                    (where((x_monteCarlo[x_outputs_list[4]]<X_target_GRID[x_outputs_list[4]][i,j,k,l,m])==True))[0]))
                                PF_correlated[i,j,k,l,m]   = len(intersect_pos)/N_realisations
                                for z in arange(len(y_mean_list)):
                                    if Y_type[y_mean_list[z]] == '1':
                                        S_pK[y_mean_list[z]][i,j,k,l,m]  = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])/(b_list_all[y_sigma_list[z]]**2))/N_realisations
                                        S_pK[y_sigma_list[z]][i,j,k,l,m] = sum(((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])**2 - b_list_all[y_sigma_list[z]]**2)/(b_list_all[y_sigma_list[z]]**3))/N_realisations
                                    elif Y_type[y_mean_list[z]] == '2':
                                        S_pK[y_mean_list[z]][i,j,k,l,m]  = sum(log(y_monteCarlo[y_mean_list[z]][intersect_pos]/b_list_all[y_sigma_list[z]])-digamma(b_list_all[y_mean_list[z]]))/N_realisations
                                        S_pK[y_sigma_list[z]][i,j,k,l,m] = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]/(b_list_all[y_sigma_list[z]]**2)) - (b_list_all[y_mean_list[z]]/b_list_all[y_sigma_list[z]]))/N_realisations

        elif len(x_outputs_list)==6:
            for i in arange(PF_correlated.shape[0]):
                for j in arange(PF_correlated.shape[1]):
                    for k in arange(PF_correlated.shape[2]):
                        for l in arange(PF_correlated.shape[3]):
                            for m in arange(PF_correlated.shape[4]):
                                for n in arange(PF_correlated.shape[5]):
                                    intersect_pos = reduce(intersect1d,((where((x_monteCarlo[x_outputs_list[0]]<X_target_GRID[x_outputs_list[0]][i,j,k,l,m,n])==True))[0],
                                                                        (where((x_monteCarlo[x_outputs_list[1]]<X_target_GRID[x_outputs_list[1]][i,j,k,l,m,n])==True))[0],
                                                                        (where((x_monteCarlo[x_outputs_list[2]]<X_target_GRID[x_outputs_list[2]][i,j,k,l,m,n])==True))[0],
                                                                        (where((x_monteCarlo[x_outputs_list[3]]<X_target_GRID[x_outputs_list[3]][i,j,k,l,m,n])==True))[0],
                                                                        (where((x_monteCarlo[x_outputs_list[4]]<X_target_GRID[x_outputs_list[4]][i,j,k,l,m,n])==True))[0],
                                                                        (where((x_monteCarlo[x_outputs_list[5]]<X_target_GRID[x_outputs_list[5]][i,j,k,l,m,n])==True))[0]))
                                    PF_correlated[i,j,k,l,m,n]   = len(intersect_pos)/N_realisations
                                    for z in arange(len(y_mean_list)):
                                        if Y_type[y_mean_list[z]] == '1':
                                            S_pK[y_mean_list[z]][i,j,k,l,m,n]  = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])/(b_list_all[y_sigma_list[z]]**2))/N_realisations
                                            S_pK[y_sigma_list[z]][i,j,k,l,m,n] = sum(((y_monteCarlo[y_mean_list[z]][intersect_pos]-b_list_all[y_mean_list[z]])**2 - b_list_all[y_sigma_list[z]]**2)/(b_list_all[y_sigma_list[z]]**3))/N_realisations
                                        elif Y_type[y_mean_list[z]] == '2':
                                            S_pK[y_mean_list[z]][i,j,k,l,m,n]  = sum(log(y_monteCarlo[y_mean_list[z]][intersect_pos]/b_list_all[y_sigma_list[z]])-digamma(b_list_all[y_mean_list[z]]))/N_realisations
                                            S_pK[y_sigma_list[z]][i,j,k,l,m,n] = sum((y_monteCarlo[y_mean_list[z]][intersect_pos]/(b_list_all[y_sigma_list[z]]**2)) - (b_list_all[y_mean_list[z]]/b_list_all[y_sigma_list[z]]))/N_realisations

        # COMPUTE JPDF FROM JCDF
        px_correlated = PF_correlated
        for i in x_outputs_list:
            px_correlated_dx = gradient(px_correlated   , x_target[i] , axis=len(x_outputs_list)-x_outputs_list.index(i)-1)
            px_correlated    = px_correlated_dx



        # COMPUTE SENSITIVITIES OF THE JPDF
        s_pk = {}
        for j in hstack((y_mean_list,y_sigma_list)):
            s_pk[j]=S_pK[j]
            for i in x_outputs_list:
                s_pk_dx = gradient(s_pk[j]   , x_target[i] , axis=len(x_outputs_list)-x_outputs_list.index(i)-1)
                s_pk[j] = s_pk_dx

        # complete with zeros
        def set_zeros(set_of_data,vlue):
            test1 = set_of_data > -1e-10
            test2 = set_of_data <  1e-10

            if len(x_outputs_list)==1:
                for i in arange(set_of_data.shape[0]):
                    if test1[i] and test2[i]:
                        set_of_data[i]=vlue

            elif len(x_outputs_list)==2:
                for i in arange(set_of_data.shape[0]):
                    for j in arange(set_of_data.shape[1]):
                        if test1[i,j] and test2[i,j]:
                            set_of_data[i,j]=vlue

            elif len(x_outputs_list)==3:
                for i in arange(set_of_data.shape[0]):
                    for j in arange(set_of_data.shape[1]):
                        for k in arange(set_of_data.shape[2]):
                            if test1[i,j,k] and test2[i,j,k]:
                                set_of_data[i,j,k]=vlue

            elif len(x_outputs_list)==4:
                for i in arange(set_of_data.shape[0]):
                    for j in arange(set_of_data.shape[1]):
                        for k in arange(set_of_data.shape[2]):
                            for l in arange(set_of_data.shape[3]):
                                if test1[i,j,k,l] and test2[i,j,k,l]:
                                    set_of_data[i,j,k,l]=vlue

            elif len(x_outputs_list)==5:
                for i in arange(set_of_data.shape[0]):
                    for j in arange(set_of_data.shape[1]):
                        for k in arange(set_of_data.shape[2]):
                            for l in arange(set_of_data.shape[3]):
                                for m in arange(set_of_data.shape[4]):
                                    if test1[i,j,k,l,m] and test2[i,j,k,l,m]:
                                        set_of_data[i,j,k,l,m]=vlue

            elif len(x_outputs_list)==6:
                for i in arange(set_of_data.shape[0]):
                    for j in arange(set_of_data.shape[1]):
                        for k in arange(set_of_data.shape[2]):
                            for l in arange(set_of_data.shape[3]):
                                for m in arange(set_of_data.shape[4]):
                                    for n in arange(set_of_data.shape[5]):
                                        if test1[i,j,k,l,m,n] and test2[i,j,k,l,m,n]:
                                            set_of_data[i,j,k,l,m,n]=vlue
        set_zeros(px_correlated,0.0000001)

        for j in hstack((y_mean_list,y_sigma_list)):
            set_zeros(s_pk[j],0)

        # compute the Fisher Information Matrix

        Gx , Gy = meshgrid(arange(len(Y_list)),arange(len(Y_list)))

        Fjk_IMP = zeros((len(Y_list),len(Y_list)))
        for j in arange(len(Y_list)):
            for k in arange(len(Y_list)):
                Integrand_IMP1 = (1/px_correlated) * s_pk[hstack((y_mean_list,y_sigma_list))[j]] * s_pk[hstack((y_mean_list,y_sigma_list))[k]]

                for i in x_outputs_list:
                    Integrand_X = trapz(Integrand_IMP1 , x_target[i] )
                    Integrand_IMP1    = Integrand_X

                Fjk_IMP[j,k]   = Integrand_X

        # normalise Fjk

        lamIM , vIM = eig(Fjk_IMP)
        Fjk_IMP_normalised = zeros((len(Y_list),len(Y_list)))
        for i in arange(len(Y_list)):
            for j in arange(len(Y_list)):
                Fjk_IMP_normalised[i,j]=Fjk_IMP[i,j]*b_list[i]*b_list[j]

        Y_list_alltext_Gaussian = [r'$\mu_{f_1}$',r'$\mu_{f_2}$',r'$\mu_{f_3}$',
                                   r'$\mu_{k_1}$',r'$\mu_{k_2}$',r'$\mu_{k_3}$',
                                   r'$\mu_{c_1}$',r'$\mu_{c_2}$',r'$\mu_{c_3}$',
                                   r'$\mu_{m_1}$',r'$\mu_{m_2}$',r'$\mu_{m_3}$',
                                   r'$\sigma_{f_1}$',r'$\sigma_{f_2}$',r'$\sigma_{f_3}$',
                                   r'$\sigma_{k_1}$',r'$\sigma_{k_2}$',r'$\sigma_{k_3}$',
                                   r'$\sigma_{c_1}$',r'$\sigma_{c_2}$',r'$\sigma_{c_3}$',
                                   r'$\sigma_{m_1}$',r'$\sigma_{m_2}$',r'$\sigma_{m_3}$']


        Y_list_alltext_Gamma    = [r'$\kappa_{f_1}$',r'$\kappa_{f_2}$',r'$\kappa_{f_3}$',
                                   r'$\kappa_{k_1}$',r'$\kappa_{k_2}$',r'$\kappa_{k_3}$',
                                   r'$\kappa_{c_1}$',r'$\kappa_{c_2}$',r'$\kappa_{c_3}$',
                                   r'$\kappa_{m_1}$',r'$\kappa_{m_2}$',r'$\kappa_{m_3}$',
                                   r'$\theta_{f_1}$',r'$\theta_{f_2}$',r'$\theta_{f_3}$',
                                   r'$\theta_{k_1}$',r'$\theta_{k_2}$',r'$\theta_{k_3}$',
                                   r'$\theta_{c_1}$',r'$\theta_{c_2}$',r'$\theta_{c_3}$',
                                   r'$\theta_{m_1}$',r'$\theta_{m_2}$',r'$\theta_{m_3}$']


        Y_listtext = []
        for i in arange(len(Y_list_alltext_Gaussian)):
            if valid_b_all[i]:
                if (Y_type+Y_type)[i]=='1':
                    Y_listtext.append(Y_list_alltext_Gaussian[i])
                elif (Y_type+Y_type)[i]=='2':
                    Y_listtext.append(Y_list_alltext_Gamma[i])

        lamIMnorm , vIMnorm = eig(Fjk_IMP_normalised)

        values_eig = []
        for i in arange(len(lamIMnorm)):
            values_eig.append('eigenvalue '+str(i+1))

    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05)
    fig.update_layout(title_text=r'$F_{jk}=b_j b_k\int \frac{1}{p(\textbf{x}, \textbf{b})}\frac{\partial p(\textbf{x}, \textbf{b})}{\partial b_k}\frac{\partial p(\textbf{x}, \textbf{b})}{\partial b_j} \textrm{d} \textbf{x} $',
                      font=dict(family='Arial, monospace', size=18, color='blue'),
                      width=800, height=700,title_x=0.5,plot_bgcolor= 'rgba(0, 0, 0, 0)'
                      ,paper_bgcolor= 'rgba(0, 0, 0, 0)')


    fig.add_contour(z=Fjk_IMP_normalised,x=arange(len(Y_list)),y=arange(len(Y_list)), row=1, col=1)

    fig.update_layout(xaxis = dict(tickmode = 'array',
                                   tickvals = arange(len(Y_list)),
                                   ticktext = Y_listtext))

    fig.update_layout(yaxis = dict(tickmode = 'array',
                                   tickvals = arange(len(Y_list)),
                                   ticktext = Y_listtext))


    graphJSONFJK = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSONeig = json.dumps(EigenBar(Y_listtext, vIMnorm,lamIMnorm,int(0)), cls=plotly.utils.PlotlyJSONEncoder)

    global num

    if 'num' not in globals():
        num = 0
    if request.method=='POST':
        for key,val in request.form.items():

            if key == "0":
                #num = 0
                pass
            elif key == "1":
                num=num-1
                if num >= 0:
                    graphJSONeig = json.dumps(EigenBar(Y_listtext, vIMnorm,lamIMnorm,int(num)), cls=plotly.utils.PlotlyJSONEncoder)
                else:
                    graphJSONeig = json.dumps(EigenBar(Y_listtext, vIMnorm,lamIMnorm,int(0)), cls=plotly.utils.PlotlyJSONEncoder)
                    num = 0
            elif key == "2":
                if num < len(Y_listtext)-1:
                    num=num+1
                    graphJSONeig = json.dumps(EigenBar(Y_listtext, vIMnorm,lamIMnorm,int(num)), cls=plotly.utils.PlotlyJSONEncoder)
                else:
                    graphJSONeig = json.dumps(EigenBar(Y_listtext, vIMnorm,lamIMnorm,int(len(Y_listtext)-1)), cls=plotly.utils.PlotlyJSONEncoder)
                    num = int(len(Y_listtext)-1)

    return render_template('design_fisher.html', form=form, plot=graphJSONFJK, plot2=graphJSONeig,date=date)

def EigenBar(Y_listtext1, vIMnorm1,lamIMnorm1,II):

    fig = make_subplots(rows=1, cols=1, shared_xaxes=False, vertical_spacing=0.1)
    fig.update_layout(width=800, height=400)



    fig.add_bar(x=Y_listtext1,y=real(vIMnorm1[:,II]), name='eigenvector', row=1, col=1)
    fig.update_layout(title_text='Eigenvalue '+str(II+1)+' = '+str("{0:.3f}".format(real(lamIMnorm1[II]))),
                      font=dict(family='Arial, monospace', size=18, color='blue'),
                      title_x=0.5,plot_bgcolor= 'rgba(0, 0, 0, 0)',
                      paper_bgcolor= 'rgba(0, 0, 0, 0)')
    fig.update_xaxes(showgrid=False, gridwidth=0.5, gridcolor='Grey',
                     zeroline=False, zerolinewidth=0.5, zerolinecolor='Grey',
                     showline=True, linewidth=1, linecolor='black')

    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='Grey',
                     zeroline=False, zerolinewidth=0.5, zerolinecolor='Grey',
                     showline=True, linewidth=1, linecolor='black')

    fig.update_layout(showlegend=False, font=dict(size=15))

    fig.update_layout(yaxis = dict(range=[-1,1.05]))

    fig.update_layout(xaxis = dict(tickmode = 'array',
                                   tickvals = list(arange(len(Y_listtext1))),
                                   ticktext = Y_listtext1))

    return fig


def testt():
    Ntop = (JPDFsize-1)
    Stp = 100/Ntop

    X_list = []
    for i in arange(int(len(X_list_all))):
        if AllOutput[i]==1:
            X_list.append(X_list_all[i])

    h1 = round(int(JPDFsize/2)*Stp,1)
    h2 = round(int(JPDFsize/2)*Stp,1)
    h3 = round(int(JPDFsize/2)*Stp,1)
    h4 = round(int(JPDFsize/2)*Stp,1)
    h5 = round(int(JPDFsize/2)*Stp,1)
    h6 = round(int(JPDFsize/2)*Stp,1)


    #graphJSONdelt = 1

    if AllOutput[0] is False:
        h1=0
    if AllOutput[1] is False:
        h2=0
    if AllOutput[2] is False:
        h3=0
    if AllOutput[3] is False:
        h4=0
    if AllOutput[4] is False:
        h5=0
    if AllOutput[5] is False:
        h6=0

    if request.method=='POST':
        req = request.form

        h1 = round(float(req.get("gain1")),1)
        h2 = round(float(req.get("gain2")),1)
        h3 = round(float(req.get("gain3")),1)
        h4 = round(float(req.get("gain4")),1)
        h5 = round(float(req.get("gain5")),1)
        h6 = round(float(req.get("gain6")),1)



        SetScale  = {0:h1,
                     1:h2,
                     2:h3,
                     3:h4,
                     4:h5,
                     5:h6}

        L=vIM
        b= b_list

        tt = hstack((y_mean_list,y_sigma_list))

        Del_Pf = {}


        for i in arange(len(L)):
            Del_P = 0*S_pK[0]
            for j in tt:
                 Del_P= Del_P + S_pK[j]*L[:,i][where(tt==j)[0][0]]
            Del_Pf[i] = Del_P



        array_contributions = zeros(len(L))


        if len(X_list)==1:
            slic = (int(round(SetScale[x_outputs_list[0]]/(100/Ntop))))
        elif len(X_list)==2:
            slic = (int(round(SetScale[x_outputs_list[0]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[1]]/(100/Ntop))))
        elif len(X_list)==3:
            slic = (int(round(SetScale[x_outputs_list[0]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[1]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[2]]/(100/Ntop))))
        elif len(X_list)==4:
            slic = (int(round(SetScale[x_outputs_list[0]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[1]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[2]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[3]]/(100/Ntop))))
        elif len(X_list)==5:
            slic = (int(round(SetScale[x_outputs_list[0]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[1]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[2]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[3]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[4]]/(100/Ntop))))
        elif len(X_list)==6:
            slic = (int(round(SetScale[x_outputs_list[0]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[1]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[2]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[3]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[4]]/(100/Ntop))),
                    int(round(SetScale[x_outputs_list[5]]/(100/Ntop))))

        for i in arange(len(L)):
            array_contributions[i]= Del_Pf[i][slic]




        Delta_Projection    = [r'$\Delta P^{1}$',r'$\Delta P^{2}$',r'$\Delta P^{3}$',r'$\Delta P^{4}$',
                               r'$\Delta P^{5}$',r'$\Delta P^{6}$',r'$\Delta P^{7}$',r'$\Delta P^{8}$',
                               r'$\Delta P^{9}$',r'$\Delta P^{10}$',r'$\Delta P^{11}$',r'$\Delta P^{12}$',
                               r'$\Delta P^{13}$',r'$\Delta P^{14}$',r'$\Delta P^{15}$',r'$\Delta P^{16}$',
                               r'$\Delta P^{17}$',r'$\Delta P^{18}$',r'$\Delta P^{19}$',r'$\Delta P^{20}$',
                               r'$\Delta P^{21}$',r'$\Delta P^{22}$',r'$\Delta P^{23}$',r'$\Delta P^{24}$']


        Delta_Projection_bar = []
        for i in arange(len(L)):
            Delta_Projection_bar.append(Delta_Projection[i])



        fig = make_subplots(rows=1, cols=1, shared_xaxes=False, vertical_spacing=0.1)
        fig.update_layout(width=800, height=400)



        fig.add_bar(x=Delta_Projection_bar,y=array_contributions, name='Contribution to the probability of failure', row=1, col=1)
        fig.update_layout( title_text=r'$\Delta P_{f}^{n}=\frac{\partial P(\textbf{x}, \textbf{b})}{\partial b_j} \textbf{q}^{(n)}$',
                           font=dict(family='Arial, monospace', size=18, color='blue'),
                          title_x=0.5,plot_bgcolor= 'rgba(0, 0, 0, 0)',
                          paper_bgcolor= 'rgba(0, 0, 0, 0)')
        fig.update_xaxes(showgrid=False, gridwidth=0.5, gridcolor='Grey',
                         zeroline=False, zerolinewidth=0.5, zerolinecolor='Grey',
                         showline=True, linewidth=1, linecolor='black')

        fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='Grey',
                         zeroline=False, zerolinewidth=0.5, zerolinecolor='Grey',
                         showline=True, linewidth=1, linecolor='black')

        fig.update_layout(showlegend=False, font=dict(size=15))

        fig.update_layout(xaxis = dict(tickmode = 'array',
                                       tickvals = list(arange(len(Delta_Projection_bar))),
                                       ticktext = Delta_Projection_bar))

        graphJSONdelt = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('design_sensitivity.html' , plot=graphJSONdelt, h1=h1, h2=h2, h3=h3, h4=h4, h5=h5, h6=h6, Stp=Stp ,date=date)

    return render_template('design_sensitivity.html' , h1=h1, h2=h2, h3=h3, h4=h4, h5=h5, h6=h6, Stp=Stp ,date=date)

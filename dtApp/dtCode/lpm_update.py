'''
This function updates the parameters of the 3dof model.
'''
from types import ModuleType
from flask import render_template, request, redirect, url_for
from dtApp import app
from dtApp import date
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
#import os


from dtLib.lpmupdate.circleFitting import circle_fit



@app.route('/lpm_update', methods=['GET','POST'])
def lpm_update():
    # request csv file from user and calulate parameters and generate profile
    if request.method == 'POST':
        f = request.files['csvfile']
        '''
        if not os.path.isdir('dtApp/dtData/frfs'):
            os.mkdir('dtApp/dtData/frfs')
        filepath = os.path.join('dtApp/dtData/frfs', f.filename)
        f.save(filepath)
        #f.save(secure_filename(f.filename))
        '''
        
        #frf = np.genfromtxt('dtApp/dtData/frfs/test_3.csv', dtype=[complex ,complex,complex,complex], delimiter=';')
        frf = np.genfromtxt(f, dtype=[complex ,complex,complex,complex], delimiter=';')

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

        dfreq = freq[1]-freq[0] # frequency increment

        # cut mobility vector around each resonance
        y1_mode1 = y1[int(4/dfreq):int(12/dfreq)]
        y1_mode2 = y1[int(12/dfreq):int(22/dfreq)]
        y1_mode3 = y1[int(22/dfreq):int(40/dfreq)]

        y2_mode1 = y2[int(4/dfreq):int(12/dfreq)]
        y2_mode2 = y2[int(12/dfreq):int(22/dfreq)]
        y2_mode3 = y2[int(22/dfreq):int(40/dfreq)]

        y3_mode1 = y3[int(4/dfreq):int(12/dfreq)]
        y3_mode2 = y3[int(12/dfreq):int(22/dfreq)]
        y3_mode3 = y3[int(22/dfreq):int(40/dfreq)]

        freq_mode1 = freq[int(4/dfreq):int(12/dfreq)]
        freq_mode2 = freq[int(12/dfreq):int(22/dfreq)]
        freq_mode3 = freq[int(22/dfreq):int(40/dfreq)]

        y1_mode1_real = np.real(y1_mode1)
        y1_mode1_imag = np.imag(y1_mode1)
        y1_mode2_real = np.real(y1_mode2)
        y1_mode2_imag = np.imag(y1_mode2)
        y1_mode3_real = np.real(y1_mode3)
        y1_mode3_imag = np.imag(y1_mode3)

        y2_mode1_real = np.real(y2_mode1)
        y2_mode1_imag = np.imag(y2_mode1)
        y2_mode2_real = np.real(y2_mode2)
        y2_mode2_imag = np.imag(y2_mode2)
        y2_mode3_real = np.real(y2_mode3)
        y2_mode3_imag = np.imag(y2_mode3)

        y3_mode1_real = np.real(y3_mode1)
        y3_mode1_imag = np.imag(y3_mode1)
        y3_mode2_real = np.real(y3_mode2)
        y3_mode2_imag = np.imag(y3_mode2)
        y3_mode3_real = np.real(y3_mode3)
        y3_mode3_imag = np.imag(y3_mode3)

        # circle fitting each mode (same for each sensor in order to calculate the mode shapes)
        modalfit_1_mode1 = circle_fit(y1_mode1_real, y1_mode1_imag) # fit circle to mobility of sensor 1 around mode 1
        xc_1_mode1 = modalfit_1_mode1['xc']
        yc_1_mode1 = modalfit_1_mode1['yc']
        r_1_mode1 = modalfit_1_mode1['r']

        modalfit_1_mode2 = circle_fit(y1_mode2_real, y1_mode2_imag) # fit circle to mobility of sensor 1 around mode 2
        xc_1_mode2 = modalfit_1_mode2['xc']
        yc_1_mode2 = modalfit_1_mode2['yc']
        r_1_mode2 = modalfit_1_mode2['r']

        modalfit_1_mode3 = circle_fit(y1_mode3_real, y1_mode3_imag) # fit circle to mobility of sensor 1 around mode 3
        xc_1_mode3 = modalfit_1_mode3['xc']
        yc_1_mode3 = modalfit_1_mode3['yc']
        r_1_mode3 = modalfit_1_mode3['r']

        modalfit_2_mode1 = circle_fit(y2_mode1_real, y2_mode1_imag) # fit circle to mobility of sensor 2 around mode 1
        xc_2_mode1 = modalfit_2_mode1['xc']
        yc_2_mode1 = modalfit_2_mode1['yc']
        r_2_mode1 = modalfit_2_mode1['r']

        modalfit_2_mode2 = circle_fit(y2_mode2_real, y2_mode2_imag) # fit circle to mobility of sensor 2 around mode 2
        xc_2_mode2 = modalfit_2_mode2['xc']
        yc_2_mode2 = modalfit_2_mode2['yc']
        r_2_mode2 = modalfit_2_mode2['r']

        modalfit_2_mode3 = circle_fit(y2_mode3_real, y2_mode3_imag) # fit circle to mobility of sensor 2 around mode 3
        xc_2_mode3 = modalfit_2_mode3['xc']
        yc_2_mode3 = modalfit_2_mode3['yc']
        r_2_mode3 = modalfit_2_mode3['r']

        modalfit_3_mode1 = circle_fit(y3_mode1_real, y3_mode1_imag) # fit circle to mobility of sensor 3 around mode 1
        xc_3_mode1 = modalfit_3_mode1['xc']
        yc_3_mode1 = modalfit_3_mode1['yc']
        r_3_mode1 = modalfit_3_mode1['r']

        modalfit_3_mode2 = circle_fit(y3_mode2_real, y3_mode2_imag) # fit circle to mobility of sensor 3 around mode 2
        xc_3_mode2 = modalfit_3_mode2['xc']
        yc_3_mode2 = modalfit_3_mode2['yc']
        r_3_mode2 = modalfit_3_mode2['r']

        modalfit_3_mode3 = circle_fit(y3_mode3_real, y3_mode3_imag) # fit circle to mobility of sensor 3 around mode 3
        xc_3_mode3 = modalfit_3_mode3['xc']
        yc_3_mode3 = modalfit_3_mode3['yc']
        r_3_mode3 = modalfit_3_mode3['r']

        theta = np.linspace(0, 2*np.pi, num=1000)


        # figures of circle fitting
        fig1 = make_subplots(rows=1, cols=1)
        fig1.update_layout(width=600, height=500)
        fig1.add_scatter(x=y1_mode1_real,y=y1_mode1_imag, name='sensor 1 mode 1', mode = 'lines', row=1, col=1)
        fig1.add_scatter(x=y1_mode2_real,y=y1_mode2_imag, name='sensor 1 mode 2', mode = 'lines', row=1, col=1)
        fig1.add_scatter(x=y1_mode3_real,y=y1_mode3_imag, name='sensor 1 mode 3', mode = 'lines', row=1, col=1)
        fig1.add_scatter(x=xc_1_mode1+r_1_mode1*np.cos(theta),y=yc_1_mode1+r_1_mode1*np.sin(theta), name='circ fit #1 mode 1', mode = 'lines', row=1, col=1)
        fig1.add_scatter(x=xc_1_mode2+r_1_mode2*np.cos(theta),y=yc_1_mode2+r_1_mode2*np.sin(theta), name='circ fit #1 mode 2', mode = 'lines', row=1, col=1)
        fig1.add_scatter(x=xc_1_mode3+r_1_mode3*np.cos(theta),y=yc_1_mode3+r_1_mode3*np.sin(theta), name='circ fit #1 mode 3', mode = 'lines', row=1, col=1)

        fig2 = make_subplots(rows=1, cols=1)
        fig2.update_layout(width=600, height=500)
        fig2.add_scatter(x=y2_mode1_real,y=y2_mode1_imag, name='sensor 2 mode 1', mode = 'lines', row=1, col=1)
        fig2.add_scatter(x=y2_mode2_real,y=y2_mode2_imag, name='sensor 2 mode 2', mode = 'lines', row=1, col=1)
        fig2.add_scatter(x=y2_mode3_real,y=y2_mode3_imag, name='sensor 2 mode 3', mode = 'lines', row=1, col=1)
        fig2.add_scatter(x=xc_2_mode1+r_2_mode1*np.cos(theta),y=yc_2_mode1+r_2_mode1*np.sin(theta), name='circ fit #2 mode 1', mode = 'lines', row=1, col=1)
        fig2.add_scatter(x=xc_2_mode2+r_2_mode2*np.cos(theta),y=yc_2_mode2+r_2_mode2*np.sin(theta), name='circ fit #2 mode 2', mode = 'lines', row=1, col=1)
        fig2.add_scatter(x=xc_2_mode3+r_2_mode3*np.cos(theta),y=yc_2_mode3+r_2_mode3*np.sin(theta), name='circ fit #2 mode 3', mode = 'lines', row=1, col=1)

        fig3 = make_subplots(rows=1, cols=1)
        fig3.update_layout(width=600, height=500)
        fig3.add_scatter(x=y3_mode1_real,y=y3_mode1_imag, name='sensor 3 mode 1', mode = 'lines', row=1, col=1)
        fig3.add_scatter(x=y3_mode2_real,y=y3_mode2_imag, name='sensor 3 mode 2', mode = 'lines', row=1, col=1)
        fig3.add_scatter(x=y3_mode3_real,y=y3_mode3_imag, name='sensor 3 mode 3', mode = 'lines', row=1, col=1)
        fig3.add_scatter(x=xc_3_mode1+r_3_mode1*np.cos(theta),y=yc_3_mode1+r_3_mode1*np.sin(theta), name='circ fit #3 mode 1', mode = 'lines', row=1, col=1)
        fig3.add_scatter(x=xc_3_mode2+r_3_mode2*np.cos(theta),y=yc_3_mode2+r_3_mode2*np.sin(theta), name='circ fit #3 mode 2', mode = 'lines', row=1, col=1)
        fig3.add_scatter(x=xc_3_mode3+r_3_mode3*np.cos(theta),y=yc_3_mode3+r_3_mode3*np.sin(theta), name='circ fit #3 mode 3', mode = 'lines', row=1, col=1)

        # Update xaxis properties
        fig1.update_xaxes(title_text="real", titlefont=dict(size=10), row=1, col=1)
        fig2.update_xaxes(title_text="real", titlefont=dict(size=10), row=1, col=1)
        fig3.update_xaxes(title_text="real", titlefont=dict(size=10), row=1, col=1)

        # Update yaxis properties
        fig1.update_yaxes(title_text="imag", titlefont=dict(size=10), row=1, col=1)
        fig2.update_yaxes(title_text="imag", titlefont=dict(size=10), row=1, col=1)
        fig3.update_yaxes(title_text="imag", titlefont=dict(size=10), row=1, col=1)

        fig1.update_layout(showlegend=True, font=dict(size=10), legend=dict(x=1.1, y=1))
        fig2.update_layout(showlegend=True, font=dict(size=10), legend=dict(x=1.1, y=1))
        fig3.update_layout(showlegend=True, font=dict(size=10), legend=dict(x=1.1, y=1))

        circfit1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        circfit2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        circfit3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

        # identify natural freqencies
        fn_1_mode1_idx = np.argmax(np.absolute(y1_mode1))
        fn_1_mode1 = freq_mode1[fn_1_mode1_idx]
        fn_1_mode2_idx = np.argmax(np.absolute(y1_mode2))
        fn_1_mode2 = freq_mode2[fn_1_mode2_idx]
        fn_1_mode3_idx = np.argmax(np.absolute(y1_mode3))
        fn_1_mode3 = freq_mode3[fn_1_mode3_idx]

        fn_2_mode1_idx = np.argmax(np.absolute(y2_mode1))
        fn_2_mode1 = freq_mode1[fn_2_mode1_idx]
        fn_2_mode2_idx = np.argmax(np.absolute(y2_mode2))
        fn_2_mode2 = freq_mode2[fn_2_mode2_idx]
        fn_2_mode3_idx = np.argmax(np.absolute(y2_mode3))
        fn_2_mode3 = freq_mode3[fn_2_mode3_idx]

        fn_3_mode1_idx = np.argmax(np.absolute(y3_mode1))
        fn_3_mode1 = freq_mode1[fn_3_mode1_idx]
        fn_3_mode2_idx = np.argmax(np.absolute(y3_mode2))
        fn_3_mode2 = freq_mode2[fn_3_mode2_idx]
        fn_3_mode3_idx = np.argmax(np.absolute(y3_mode3))
        fn_3_mode3 = freq_mode3[fn_3_mode3_idx]

        fn_mode1 = np.average([fn_1_mode1, fn_2_mode1, fn_3_mode1])
        fn_mode2 = np.average([fn_1_mode2, fn_2_mode2, fn_3_mode2])
        fn_mode3 = np.average([fn_1_mode3, fn_2_mode3, fn_3_mode3])

        # identify damping ratios
        delta_freq_point = 1
        # sensor 1
        fc = freq_mode1[fn_1_mode1_idx-delta_freq_point]
        fd = freq_mode1[fn_1_mode1_idx+delta_freq_point]
        thetac = np.angle(y1_mode1[fn_1_mode1_idx])-np.angle(y1_mode1[fn_1_mode1_idx-delta_freq_point])
        thetad = np.angle(y1_mode1[fn_1_mode1_idx])-np.angle(y1_mode1[fn_1_mode1_idx+delta_freq_point])
        eta_1_mode1 = np.absolute(fc**2-fd**2)/(fn_1_mode1**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        fc = freq_mode2[fn_1_mode2_idx-delta_freq_point]
        fd = freq_mode2[fn_1_mode2_idx+delta_freq_point]
        thetac = np.angle(y1_mode2[fn_1_mode2_idx])-np.angle(y1_mode2[fn_1_mode2_idx-delta_freq_point])
        thetad = np.angle(y1_mode2[fn_1_mode2_idx])-np.angle(y1_mode2[fn_1_mode2_idx+delta_freq_point])
        eta_1_mode2 = np.absolute(fc**2-fd**2)/(fn_1_mode2**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        fc = freq_mode3[fn_1_mode3_idx-delta_freq_point]
        fd = freq_mode3[fn_1_mode3_idx+delta_freq_point]
        thetac = np.angle(y1_mode3[fn_1_mode3_idx])-np.angle(y1_mode3[fn_1_mode3_idx-delta_freq_point])
        thetad = np.angle(y1_mode3[fn_1_mode3_idx])-np.angle(y1_mode3[fn_1_mode3_idx+delta_freq_point])
        eta_1_mode3 = np.absolute(fc**2-fd**2)/(fn_1_mode3**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        # sensor 2
        fc = freq_mode1[fn_2_mode1_idx-delta_freq_point]
        fd = freq_mode1[fn_2_mode1_idx+delta_freq_point]
        thetac = np.angle(y2_mode1[fn_2_mode1_idx])-np.angle(y2_mode1[fn_2_mode1_idx-delta_freq_point])
        thetad = np.angle(y2_mode1[fn_2_mode1_idx])-np.angle(y2_mode1[fn_2_mode1_idx+delta_freq_point])
        eta_2_mode1 = np.absolute(fc**2-fd**2)/(fn_2_mode1**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        fc = freq_mode2[fn_2_mode2_idx-delta_freq_point]
        fd = freq_mode2[fn_2_mode2_idx+delta_freq_point]
        thetac = np.angle(y2_mode2[fn_2_mode2_idx])-np.angle(y2_mode2[fn_2_mode2_idx-delta_freq_point])
        thetad = np.angle(y2_mode2[fn_2_mode2_idx])-np.angle(y2_mode2[fn_2_mode2_idx+delta_freq_point])
        eta_2_mode2 = np.absolute(fc**2-fd**2)/(fn_2_mode2**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        fc = freq_mode3[fn_2_mode3_idx-delta_freq_point]
        fd = freq_mode3[fn_2_mode3_idx+delta_freq_point]
        thetac = np.angle(y2_mode3[fn_2_mode3_idx])-np.angle(y2_mode3[fn_2_mode3_idx-delta_freq_point])
        thetad = np.angle(y2_mode3[fn_2_mode3_idx])-np.angle(y2_mode3[fn_2_mode3_idx+delta_freq_point])
        eta_2_mode3 = np.absolute(fc**2-fd**2)/(fn_2_mode3**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        # sensor 3
        fc = freq_mode1[fn_3_mode1_idx-delta_freq_point]
        fd = freq_mode1[fn_3_mode1_idx+delta_freq_point]
        thetac = np.angle(y3_mode1[fn_3_mode1_idx])-np.angle(y3_mode1[fn_3_mode1_idx-delta_freq_point])
        thetad = np.angle(y3_mode1[fn_3_mode1_idx])-np.angle(y3_mode1[fn_3_mode1_idx+delta_freq_point])
        eta_3_mode1 = np.absolute(fc**2-fd**2)/(fn_3_mode1**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        fc = freq_mode2[fn_3_mode2_idx-delta_freq_point]
        fd = freq_mode2[fn_3_mode2_idx+delta_freq_point]
        thetac = np.angle(y3_mode2[fn_3_mode2_idx])-np.angle(y3_mode2[fn_3_mode2_idx-delta_freq_point])
        thetad = np.angle(y3_mode2[fn_3_mode2_idx])-np.angle(y3_mode2[fn_3_mode2_idx+delta_freq_point])
        eta_3_mode2 = np.absolute(fc**2-fd**2)/(fn_3_mode2**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        fc = freq_mode3[fn_3_mode3_idx-delta_freq_point]
        fd = freq_mode3[fn_3_mode3_idx+delta_freq_point]
        thetac = np.angle(y3_mode3[fn_3_mode3_idx])-np.angle(y3_mode3[fn_3_mode3_idx-delta_freq_point])
        thetad = np.angle(y3_mode3[fn_3_mode3_idx])-np.angle(y3_mode3[fn_3_mode3_idx+delta_freq_point])
        eta_3_mode3 = np.absolute(fc**2-fd**2)/(fn_3_mode3**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))

        eta_mode1 = np.average([eta_1_mode1, eta_2_mode1, eta_3_mode1])
        eta_mode2 = np.average([eta_1_mode2, eta_2_mode2, eta_3_mode2])
        eta_mode3 = np.average([eta_1_mode3, eta_2_mode3, eta_3_mode3])
        
        # identify mode shapes
        mode1 = [r_1_mode1*np.sign(xc_1_mode1), r_2_mode1*np.sign(xc_2_mode1), r_3_mode1*np.sign(xc_3_mode1)]
        mode2 = [r_1_mode2*np.sign(xc_1_mode2), r_2_mode2*np.sign(xc_2_mode2), r_3_mode2*np.sign(xc_3_mode2)]
        mode3 = [r_1_mode3*np.sign(xc_1_mode3), r_2_mode3*np.sign(xc_2_mode3), r_3_mode3*np.sign(xc_3_mode3)]

        mode1_inf = mode1/np.linalg.norm(mode1, ord=np.inf) # normalise mode shapes ()
        mode2_inf = mode2/np.linalg.norm(mode2, ord=np.inf)
        mode3_inf = mode3/np.linalg.norm(mode3, ord=np.inf)

        mode1 = mode1/np.linalg.norm(mode1, ord=2) # normalise mode shapes
        mode2 = mode2/np.linalg.norm(mode2, ord=2)
        mode3 = mode3/np.linalg.norm(mode3, ord=2)

        # calculate system matrices
        ms = np.block([[mode1], [mode2], [mode3]])
        ms = ms.transpose()

        MM = np.linalg.inv(ms@ms.transpose())*5
        wn = 2*np.pi*np.array([fn_mode1, fn_mode2, fn_mode3])
        wn2 = np.diag(np.square(wn))
        KK = np.linalg.inv(ms@(np.linalg.inv(wn2)@ms.transpose()))*5
        dr = np.array([eta_mode1, eta_mode2, eta_mode3])
        CM = np.diag(2*dr*wn) # C/M = 2*xi*wn
        CC = (np.linalg.inv(ms.transpose())@CM)@np.linalg.inv(ms)*5 # identified damping matrix
        #print(MM)
        #print(KK)
        #print(CC)

        # calculate model parameters
        MM1=MM[0][0]
        MM2=MM[1][1]
        MM3=MM[2][2]

        KK3 = (KK[2][2]-KK[2][1]-KK[1][2])/3
        KK2 = (KK[1][1]-KK3-KK[1][0]-KK[0][1])/3
        KK1 = KK[0][0]-KK2
            
        CC3 = (CC[2][2]-CC[2][1]-CC[1][2])/3
        CC2 = (CC[1][1]-CC3-CC[1][0]-CC[0][1])/3
        CC1 = CC[0][0]-CC2

        # compare 3-dof model frf with experimental frf

        # generate profile and save to csv in folder Cristallo\dtApp\dtData\profiles
        profile = np.array([[MM1, MM2, MM3], [KK1, KK2, KK3], [CC1, CC2, CC3]])
        #profilename = 
        np.savetxt('..\Cristallo\dtApp\dtData\profiles\profile_'+f.filename, profile, fmt='%.4f', delimiter=';', newline='\n', header='', footer='', comments='# ', encoding=None)

        return render_template('lpm_update.html', plot1=circfit1, plot2=circfit2, plot3=circfit3, fn1="{:.2f}".format(fn_mode1), fn2="{:.2f}".format(fn_mode2), fn3="{:.2f}".format(fn_mode3), eta1="{:.4f}".format(eta_mode1), eta2="{:.4f}".format(eta_mode2), eta3="{:.4f}".format(eta_mode3), mode1=mode1_inf.reshape(3,1), mode2=mode2_inf.reshape(3,1), mode3=mode3_inf.reshape(3,1), m1="{:.2f}".format(MM1), m2="{:.2f}".format(MM2), m3="{:.2f}".format(MM3), k1="{:.2f}".format(KK1), k2="{:.2f}".format(KK2), k3="{:.2f}".format(KK3), c1="{:.2f}".format(CC1), c2="{:.2f}".format(CC2), c3="{:.2f}".format(CC3), date=date)

    #return render_template('lpm_update.html', plot1=circfit1, plot2=circfit2, plot3=circfit3, fn1="{:.2f}".format(fn_mode1), fn2="{:.2f}".format(fn_mode2), fn3="{:.2f}".format(fn_mode3), eta1="{:.4f}".format(eta_mode1), eta2="{:.4f}".format(eta_mode2), eta3="{:.4f}".format(eta_mode3), mode1=mode1_inf.reshape(3,1), mode2=mode2_inf.reshape(3,1), mode3=mode3_inf.reshape(3,1), m1="{:.2f}".format(MM1), m2="{:.2f}".format(MM2), m3="{:.2f}".format(MM3), k1="{:.2f}".format(KK1), k2="{:.2f}".format(KK2), k3="{:.2f}".format(KK3), c1="{:.2f}".format(CC1), c2="{:.2f}".format(CC2), c3="{:.2f}".format(CC3), date=date)
    return render_template('lpm_update.html', date=date)
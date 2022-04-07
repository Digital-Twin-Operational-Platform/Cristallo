'''
This tool is for the reading of live sensor data
'''
from numpy import *
from flask import render_template, request, redirect, url_for,send_file
from dtApp import app
from dtApp import date
import ctypes
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
import numpy as np
import json,time
from pathlib import Path
from openpyxl import Workbook   

@app.route('/live',methods=['GET','POST'])
def Monitor():
    if request.method=='GET': # Initial load
        sample=10e3  # Hz
        time0=1.0   #Seconds
        
        fig = make_subplots(rows=2, cols=2)
        plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template("live.html",rate=sample,Dur=time0,SCOP=plot)
    elif request.method=='POST': # Active Reading
        req = request.form
        
        SamplerateIntake = float(req.get("SamplerateIntake"))
        BuffertimeIntake = float(req.get("BuffertimeIntake"))
        Nbuffers = int(req.get("Nbuffers"))
        #Variables
        
        
        Samplerate=SamplerateIntake/1e6   #convert to microseconds #Hz samples/s(<1) Default=0.04
        Buffertime=BuffertimeIntake*1e6 #convert to microseconds(us)/buffer   （>125)
        SampleInterval=int(1/(Samplerate)*1e6) #convert to ps
        Sizebuffer=int(Buffertime*Samplerate)
        print("Buffersize %s " % Sizebuffer)
        print("SampleInterval %s PS"  %SampleInterval)
        
        # Pico set up
                
        # Create chandle and status ready for use
        chandle = ctypes.c_int16()
        status = {}
        
        # Open PicoScope 2000 Series device
        # Returns handle to chandle for use in future API functions
        status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)
        
        try:
            assert_pico_ok(status["openunit"])
        except:
        
            powerStatus = status["openunit"]
        
            if powerStatus == 286:
                status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
            else:
                raise
        
            assert_pico_ok(status["changePowerSource"])
        
        enabled = 1
        analogue_offset = 0.0
        #%% Channel set up
        # Set up channel A
        channel_range = 7
        status["setChA"] = ps.ps4000aSetChannel(chandle,
                                                ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'],
                                                enabled,
                                                ps.PS4000A_COUPLING['PS4000A_DC'],
                                                channel_range,
                                                analogue_offset)
        assert_pico_ok(status["setChA"])
        # Set up channel B
        status["setChB"] = ps.ps4000aSetChannel(chandle,
                                                ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'],
                                                enabled,
                                                ps.PS4000A_COUPLING['PS4000A_DC'],
                                                channel_range,
                                                analogue_offset)
        assert_pico_ok(status["setChB"])
        # Set up channel C
        channel_range = 7
        status["setChC"] = ps.ps4000aSetChannel(chandle,
                                                ps.PS4000A_CHANNEL['PS4000A_CHANNEL_C'],
                                                enabled,
                                                ps.PS4000A_COUPLING['PS4000A_DC'],
                                                channel_range,
                                                analogue_offset)
        assert_pico_ok(status["setChC"])
        
        # Set up channel D
        
        channel_range = 7
        status["setChD"] = ps.ps4000aSetChannel(chandle,
                                                ps.PS4000A_CHANNEL['PS4000A_CHANNEL_D'],
                                                enabled,
                                                ps.PS4000A_COUPLING['PS4000A_DC'],
                                                channel_range,
                                                analogue_offset)
        assert_pico_ok(status["setChD"])
        #%%Buffer set up
        # Size of capture
        sizeOfOneBuffer = Sizebuffer
        numBuffersToCapture = Nbuffers
        
        totalSamples = sizeOfOneBuffer * numBuffersToCapture
        
        for i in range(Nbuffers):
            # Create buffers ready for assigning pointers for data collection
            bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
            bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
            bufferCMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
            bufferDMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
            
            memory_segment = 0
            # Set data buffer location for data collection from channel A
            status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(chandle,
                                                                 ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'],
                                                                 bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                                 None,
                                                                 sizeOfOneBuffer,
                                                                 memory_segment,
                                                                 ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
            assert_pico_ok(status["setDataBuffersA"])
            # Set data buffer location for data collection from channel B
            status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(chandle,
                                                                 ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'],
                                                                 bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                                 None,
                                                                 sizeOfOneBuffer,
                                                                 memory_segment,
                                                                 ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
            assert_pico_ok(status["setDataBuffersB"])
            # Set data buffer location for data collection from channel C
            status["setDataBuffersC"] = ps.ps4000aSetDataBuffers(chandle,
                                                                 ps.PS4000A_CHANNEL['PS4000A_CHANNEL_C'],
                                                                 bufferCMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                                 None,
                                                                 sizeOfOneBuffer,
                                                                 memory_segment,
                                                                 ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
            assert_pico_ok(status["setDataBuffersC"])
            # Set data buffer location for data collection from channel 
            status["setDataBuffersD"] = ps.ps4000aSetDataBuffers(chandle,
                                                                 ps.PS4000A_CHANNEL['PS4000A_CHANNEL_D'],
                                                                 bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                                 None,
                                                                 sizeOfOneBuffer,
                                                                 memory_segment,
                                                                 ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
            assert_pico_ok(status["setDataBuffersD"])
        
            # Begin streaming mode:
            sampleInterval = ctypes.c_int32(SampleInterval)
            sampleUnits = ps.PS4000A_TIME_UNITS['PS4000A_PS']
            # We are not triggering:
            maxPreTriggerSamples = 0
            autoStopOn = 1
            # No downsampling:
            downsampleRatio = 1
            status["runStreaming"] = ps.ps4000aRunStreaming(chandle,
                                                            ctypes.byref(sampleInterval),
                                                            sampleUnits,
                                                            maxPreTriggerSamples,
                                                            Sizebuffer,
                                                            autoStopOn,
                                                            downsampleRatio,
                                                            ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'],
                                                            sizeOfOneBuffer)
            assert_pico_ok(status["runStreaming"])
            
            actualSampleInterval = sampleInterval.value
            actualSampleIntervalNs = actualSampleInterval / 1000
            # We need a big buffer, not registered with the driver, to keep our complete capture in.
            bufferCompleteA = np.zeros(shape=Sizebuffer, dtype=np.int16)
            bufferCompleteB = np.zeros(shape=Sizebuffer, dtype=np.int16)
            bufferCompleteC = np.zeros(shape=Sizebuffer, dtype=np.int16)
            bufferCompleteD = np.zeros(shape=Sizebuffer, dtype=np.int16)
            global nextSample
            nextSample = 0
            autoStopOuter = False
            wasCalledBack = False
            
            def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
                global nextSample, autoStopOuter, wasCalledBack
                wasCalledBack = True
                destEnd = nextSample + noOfSamples
                sourceEnd = startIndex + noOfSamples
                bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
                bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
                bufferCompleteC[nextSample:destEnd] = bufferCMax[startIndex:sourceEnd]
                bufferCompleteD[nextSample:destEnd] = bufferDMax[startIndex:sourceEnd]
                nextSample += noOfSamples
                if autoStop:
                    autoStopOuter = True
            
        #%%Data convertion    
            # Convert the python function into a C function pointer.
            cFuncPtr = ps.StreamingReadyType(streaming_callback)
            # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
            while nextSample < totalSamples and not autoStopOuter:
                wasCalledBack = False
                status["getStreamingLastestValues"] = ps.ps4000aGetStreamingLatestValues(chandle, cFuncPtr, None)
                if not wasCalledBack:
                    # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
                    # again.
                    time.sleep(0.01)
            
            print("Done grabbing values.")
            
            # Find maximum ADC count value
            maxADC = ctypes.c_int16()
            status["maximumValue"] = ps.ps4000aMaximumValue(chandle, ctypes.byref(maxADC))
            assert_pico_ok(status["maximumValue"])
            
            # Convert ADC counts data to mV
            adc2mVChAMax = adc2mV(bufferCompleteA, channel_range, maxADC)
            adc2mVChBMax = adc2mV(bufferCompleteB, channel_range, maxADC)
            adc2mVChCMax = adc2mV(bufferCompleteC, channel_range, maxADC)
            adc2mVChDMax = adc2mV(bufferCompleteD, channel_range, maxADC)
            
            # Create time data
            time0 = np.linspace(0, (Sizebuffer) * actualSampleIntervalNs/1e9, Sizebuffer)
        
            fig = make_subplots(rows=2, cols=2, subplot_titles=("Hammer","1 floor","2 Floor","3 Floor"), shared_xaxes=False)
            fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChAMax[:])/2.25, mode='lines', name='Hammers'))
            fig.update_yaxes(title_text='Force [N]', titlefont=dict(size=14), row=1, col=1) # fig.update_xaxes(type="log")
            fig.update_xaxes(title_text='Time [s]', titlefont=dict(size=14), row=1, col=1)
            
            fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChBMax[:])/10.27, mode='lines', name='1 floor'),row=1, col=2)
            fig.update_yaxes(title_text='Acceleration [g]', titlefont=dict(size=14), row=1, col=2) # fig.update_xaxes(type="log")
            fig.update_xaxes(title_text='Time [s]', titlefont=dict(size=14), row=1, col=2)
            
            fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChCMax[:])/10.17, mode='lines', name='2 Floor'),row=2, col=1)
            fig.update_yaxes(title_text='Acceleration [g]', titlefont=dict(size=14), row=2, col=1) # fig.update_xaxes(type="log")
            fig.update_xaxes(title_text='Time [s]', titlefont=dict(size=14), row=2, col=1)
            
            fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChDMax[:])/10.33, mode='lines', name='3 Floor'),row=2, col=2)
            fig.update_yaxes(title_text='Acceleration [g]', titlefont=dict(size=14), row=2, col=2) # fig.update_xaxes(type="log")
            fig.update_xaxes(title_text='Time [s]', titlefont=dict(size=14), row=2, col=2)
            
            fig.update_layout(title_text="Streaming Graph",\
            showlegend=True,\
            font=dict(size=14),\
            plot_bgcolor= 'rgba(0, 0, 0, 0.1)',paper_bgcolor= 'rgba(0, 0, 0, 0)') #paper_bgcolor= 'rgba(0, 0, 0, 0.05)'
                        
            sideplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            ActualSamplerate=1/((time0[15]-time0[0])/15)
  
            path = "dtApp/dtData/SensorReadings.csv"
            if (Path(path)).is_file():
                pass    
            else:
                f = open(path, "x")
                f.close()
            
            #f = open(path, "w")
            workbook=Workbook()
            sheet=workbook.active
            sheet["A1"]="Time"
            sheet["B1"]="Channal A"
            sheet["C1"]="Channal B"
            sheet["D1"]="Channal C"
            sheet["E1"]="Channal D"
            sheet["F1"]="Buffersize"
            sheet["G1"]="SampleInterval Ps"
            sheet["H1"]="ActualSamplerate Hz"
            # a=time0
            # b=adc2mVChBMax[:]
            for i in range(len(time0)):
                sheet["A"+str(i+2)]=time0[i]
                sheet["B"+str(i+2)]=adc2mVChAMax[:][i]
                sheet["C"+str(i+2)]=adc2mVChBMax[:][i]
                sheet["D"+str(i+2)]=adc2mVChCMax[:][i]
                sheet["E"+str(i+2)]=adc2mVChDMax[:][i]
            sheet["F2"]= Sizebuffer 
            sheet["G2"]= SampleInterval
            sheet["H2"]= ActualSamplerate
            workbook.save(filename=path)
            
            #f.close()

            #%% Stop the scope
            # handle = chandle
            status["stop"] = ps.ps4000aStop(chandle)
            assert_pico_ok(status["stop"])
            
            # Disconnect the scope
            # handle = chandle
            status["close"] = ps.ps4000aCloseUnit(chandle)
            assert_pico_ok(status["close"])
            
            print('Saved File as '+path)
        return render_template('live.html', rate=ActualSamplerate,Dur=time0[-1],SCOP=sideplot)                    
   
@app.route('/Sensordownload')
def livedownloadFile():
#For windows you need to use drive name [ex: F:/Example.pdf]
    path = "dtApp/dtData/SensorReadings.csv"
    path_d = "dtData/SensorReadings.csv"
    if (Path(path)).is_file():
        pass    
    else:
        return 'File not found'
    
    
    print('Read file '+path)
    
    return send_file(path_d, as_attachment=True)

#%%Database Analysis
@app.route('/database',methods=['GET','POST'])
def Reader():
    if request.method=='GET': # Initial load
        sample=10e3  # Hz
        time0=1.0   #Seconds
        
        fig = make_subplots(rows=2, cols=2)
        plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template("live.html",rate=sample,Dur=time0,SCOP=plot)
    elif request.method=='POST': # Active Reading
        req = request.form  
        
        
        from sqlalchemy import event
        def init_search_path(connection, conn_record):
            cursor = connection.cursor()
            try:
                cursor.execute('SET search_path TO new_db_schema;')
            finally:
                cursor.close()
        
        
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Table, Column, String, Integer, Numeric, ForeignKey, DateTime, MetaData, ARRAY, select
        from datetime import datetime
        from sqlalchemy.orm import Session
        import numpy as np
        from sqlalchemy.ext.automap import automap_base
        base=automap_base()
        engine = create_engine("postgresql+psycopg2://postgres:d1g1tw1n@localhost:5432",echo=True)
        connection  = engine.connect()
        event.listen(engine, 'connect', init_search_path)
        Base = declarative_base()
        metadata = MetaData()
        session = Session(engine)
        
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session=Session()
        base.prepare(engine,reflect=True)
        
        r = int(np.abs(session.query(base.classes.try1.id).first()))
        
        print(r)
        
        adc2mVChAMax1 = session.query(base.classes.try1.Channala).filter(base.classes.try1.id==r).all()
        adc2mVChBMax1 = session.query(base.classes.try1.Channalb).filter(base.classes.try1.id==r).all()
        adc2mVChCMax1 = session.query(base.classes.try1.Channalc).filter(base.classes.try1.id==r).all()
        adc2mVChDMax1 = session.query(base.classes.try1.Channald).filter(base.classes.try1.id==r).all()
        Sizebuffer = session.query(base.classes.try1.Buffersize).filter(base.classes.try1.id==r).all()
        SampleInterval = session.query(base.classes.try1.SampleInterval).filter(base.classes.try1.id==1).all()
        time01 = session.query(base.classes.try1.Time).filter(base.classes.try1.id==1).all()
        
        adc2mVChAMax = np.array(np.array(adc2mVChAMax1[0])[0])
        adc2mVChBMax = np.array(np.array(adc2mVChBMax1[0])[0])
        adc2mVChCMax = np.array(np.array(adc2mVChCMax1[0])[0])
        adc2mVChDMax = np.array(np.array(adc2mVChDMax1[0])[0])
        time0 = np.array(np.array(time01[0])[0])
        
        session.close()
        
        import matplotlib.pyplot as plt
        plt.figure(num=0,clear=True)
        plt.plot(time0, adc2mVChAMax[:],label='Hammer')
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (mV)')
        plt.show()
        
        plt.figure(num=1,clear=True)
        plt.plot(time0, adc2mVChBMax[:],label='1st floor')
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (mV)')
        plt.show()
        
        plt.figure(num=2,clear=True)
        plt.plot(time0, adc2mVChCMax[:],label='2nd floor')
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (mV)')
        plt.show()
        
        plt.figure(num=3,clear=True)
        plt.plot(time0, adc2mVChDMax[:],label='3rd floor')
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (mV)')
        plt.show()
    
        #time.sleep(Sleeptime)
            
        import plotly.graph_objects as go
        import numpy
        import plotly
        from plotly.subplots import make_subplots
        import json
        
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=("Hammer","1 floor","2 Floor","3 Floor"), shared_xaxes=False)
        #fig.add_trace(go.Scatter(x=3, y=adc2mVChAMax[:], mode='markers', name='markers'))
        #fig.add_trace(go.Scatter(x=[7,9,0], y=[1,2,3], mode='markers', name='markers'))
        fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChAMax[:])/2.25, mode='lines', name='Hammers'))
        fig.update_yaxes(title_text='[N]', titlefont=dict(size=14), row=1, col=1) # fig.update_xaxes(type="log")
        fig.update_xaxes(title_text='[Time(s)]', titlefont=dict(size=14), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChBMax[:])/10.27, mode='lines', name='1 floor'),row=1, col=2)
        fig.update_yaxes(title_text='[Acceleration(g)]', titlefont=dict(size=14), row=1, col=2) # fig.update_xaxes(type="log")
        fig.update_xaxes(title_text='[Time(s)]', titlefont=dict(size=14), row=1, col=2)
        
        fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChCMax[:])/10.17, mode='lines', name='2 Floor'),row=2, col=1)
        fig.update_yaxes(title_text='[Acceleration(g)]', titlefont=dict(size=14), row=2, col=1) # fig.update_xaxes(type="log")
        fig.update_xaxes(title_text='[Time(s)]', titlefont=dict(size=14), row=2, col=1)
        
        fig.add_trace(go.Scatter(x=time0, y=np.array(adc2mVChDMax[:])/10.33, mode='lines', name='3 Floor'),row=2, col=2)
        fig.update_yaxes(title_text='[Acceleration(g)]', titlefont=dict(size=14), row=2, col=2) # fig.update_xaxes(type="log")
        fig.update_xaxes(title_text='[Time(s)]', titlefont=dict(size=14), row=2, col=2)
        
        fig.update_layout(title_text="Bounds on displacement Frequency Response Function (FRF)",\
        showlegend=True,\
        font=dict(size=14),\
        plot_bgcolor= 'rgba(0, 0, 0, 0.1)',paper_bgcolor= 'rgba(0, 0, 0, 0)') #paper_bgcolor= 'rgba(0, 0, 0, 0.05)'
                    
        sideplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        fig.show()
        
        # import plotly.offline as of
        # of.plot(fig)
        ActualSamplerate=1/((time0[15]-time0[0])/15)
        
#%%Circilar Fit
@app.route('/Circlefit',methods=['GET','POST'])
def Reader():
    if request.method=='GET': # Initial load
        sample=10e3  # Hz
        time0=1.0   #Seconds
        
        fig = make_subplots(rows=2, cols=2)
        plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template("live.html",rate=sample,Dur=time0,SCOP=plot)
    elif request.method=='POST': # Active Reading
        req = request.form  
        
        from sqlalchemy import event
        def init_search_path(connection, conn_record):
            cursor = connection.cursor()
            try:
                cursor.execute('SET search_path TO new_db_schema;')
            finally:
                cursor.close()
        
        
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Table, Column, String, Integer, Numeric, ForeignKey, DateTime, MetaData, ARRAY, select
        from datetime import datetime
        from sqlalchemy.orm import Session
        import numpy as np
        from sqlalchemy.ext.automap import automap_base
        base=automap_base()
        engine = create_engine("postgresql+psycopg2://postgres:d1g1tw1n@localhost:5432",echo=True)
        connection  = engine.connect()
        event.listen(engine, 'connect', init_search_path)
        Base = declarative_base()
        metadata = MetaData()
        session = Session(engine)
        
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session=Session()
        base.prepare(engine,reflect=True)
        
        r = int(np.abs(session.query(base.classes.try1.id).first()))
        
        print(r)
        
        adc2mVChAMax1 = session.query(base.classes.try1.Channala).filter(base.classes.try1.id==r).all()
        adc2mVChBMax1 = session.query(base.classes.try1.Channalb).filter(base.classes.try1.id==r).all()
        adc2mVChCMax1 = session.query(base.classes.try1.Channalc).filter(base.classes.try1.id==r).all()
        adc2mVChDMax1 = session.query(base.classes.try1.Channald).filter(base.classes.try1.id==r).all()
        Sizebuffer = session.query(base.classes.try1.Buffersize).filter(base.classes.try1.id==r).all()
        SampleInterval = session.query(base.classes.try1.SampleInterval).filter(base.classes.try1.id==1).all()
        time01 = session.query(base.classes.try1.Time).filter(base.classes.try1.id==1).all()
        
        adc2mVChAMax = np.array(np.array(adc2mVChAMax1[0])[0])
        adc2mVChBMax = np.array(np.array(adc2mVChBMax1[0])[0])
        adc2mVChCMax = np.array(np.array(adc2mVChCMax1[0])[0])
        adc2mVChDMax = np.array(np.array(adc2mVChDMax1[0])[0])
        time0 = np.array(np.array(time01[0])[0])
        
        session.close()
        #%%FunctionCF
        #from numpy import *
        from scipy import optimize

        # == METHOD 2b ==
        method_2b  = "leastsq with jacobian"

        def circle_fit(x,y):
            """Circle fitting the data (real and imaginary parts of the accelerance [g/N])"""
            # coordinates of the barycenter
            def calc_R(xc, yc):
                """ calculate the distance of each data points from the center (xc, yc) """
                return sqrt((x-xc)**2 + (y-yc)**2)

            def f_2b(c):
                """ calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) """
                Ri = calc_R(*c)
                return Ri - Ri.mean()

            def Df_2b(c):
                """ Jacobian of f_2b
                The axis corresponding to derivatives must be coherent with the col_deriv option of leastsq"""
                xc, yc     = c
                df2b_dc    = empty((len(c), x.size))

                Ri = calc_R(xc, yc)
                df2b_dc[0] = (xc - x)/Ri                   # dR/dxc
                df2b_dc[1] = (yc - y)/Ri                   # dR/dyc
                df2b_dc    = df2b_dc - df2b_dc.mean(axis=1)[:, newaxis]

                return df2b_dc

            x_m = mean(x)
            y_m = mean(y)
            center_estimate = x_m, y_m
            center_2b, ier = optimize.leastsq(f_2b, center_estimate, Dfun=Df_2b, col_deriv=True)

            xc_2b, yc_2b = center_2b
            Ri_2b        = calc_R(*center_2b)
            R_2b         = Ri_2b.mean()
            # residu_2b    = sum((Ri_2b - R_2b)**2)

            return {'xc': xc_2b, 'yc': yc_2b, 'r':R_2b}

        #%%Circular Fit
        import matplotlib.pyplot as plt
        import numpy as np
        from scipy import optimize
        import csv
        #from FunctionCF 
        #import circle_fit
        #%% User Parameters
        # path='MAST_tests_25-03-2022/5Hz_70Hz_0.1ms-2_300mm_beam_2.csv'
        # # ModeRanges=[[10,25],[38,42],[55,65]] # Scenario 1
        ModeRanges=[[15,18]] # Scenario 2.5
        # ModeRanges=[[9.25,9.75],[29,32],[33,37]]# Scenario 2.5
        # scenario=2.5
        # HitNum=1
        #%% Import Raw Time History
        channels=['channala','channalb','channalc','channald']
        HitNum=1
        inc=(HitNum-1)*len(channels)

        h1 = np.array(adc2mVChAMax) / 2.25
        h2 = np.array(adc2mVChBMax) / 10.16
        h3 = np.array(adc2mVChCMax) / 10.24
        h4 = np.array(adc2mVChDMax) / 10.31
        time0 = np.array(np.array(time01[0])[0])
        DATA=[h1,h2,h3,h4]
        sf=2048

        nsamples=len(h1)
        time = np.arange(0,nsamples/sf,1/sf)
        LDATA=len(channels)
            
        # %% Convert to FRF
        FRF=[]
        for i in range(LDATA):
            Y=DATA[i]
            resp=np.fft.fft(Y)
            freq=np.fft.fftfreq(time.shape[-1],d=1/sf)
            resp,freq=resp[:int(len(resp)/2)],freq[:int(len(resp)/2)]
            FRF.append(resp)
        # Get linear frequency
        freq = np.real(freq)    # frequency vector [Hz]
        w = 2*np.pi*freq
        dfreq=freq[1]-freq[0]
        theta = np.linspace(0, 2*np.pi, num=1000)
        delta_freq_point = 1
        #%% Multi Mode Extraction
        for ModeIndex in range(len(ModeRanges)):
            freq_mode = freq[int(ModeRanges[ModeIndex][0]/dfreq):int(ModeRanges[ModeIndex][1]/dfreq)]
            
            r_mode,xc_mode,yc_mode=np.zeros(LDATA),np.zeros(LDATA),np.zeros(LDATA)
            fn_mode,eta_mode,shape_mode=np.zeros(LDATA),np.zeros(LDATA),np.zeros(LDATA)
            for i in range(LDATA):
                y = FRF[i]/(1j*w)
                y_mode = y[int(ModeRanges[ModeIndex][0]/dfreq):int(ModeRanges[ModeIndex][1]/dfreq)]
                y_mode_real = np.real(y_mode)
                y_mode_imag = np.imag(y_mode)
                modalfit= circle_fit(y_mode_real, y_mode_imag) # fit circle to mobility of sensor 1 around mode 1
                xc_mode[i] = modalfit['xc']
                yc_mode[i] = modalfit['yc']
                r_mode[i] = modalfit['r']
                # Natural Frequency 
                idx = np.argmax(np.absolute(y_mode))
                fn_mode[i] = freq_mode[idx]
                # Damping Ratio
                fc = freq_mode[idx-delta_freq_point]
                fd = freq_mode[idx+delta_freq_point]
                thetac = np.angle(y_mode[idx])-np.angle(y_mode[idx-delta_freq_point])
                thetad = np.angle(y_mode[idx])-np.angle(y_mode[idx+delta_freq_point])
                eta_mode[i] = np.absolute(fc**2-fd**2)/(fn_mode[i]**2*(np.absolute(np.tan(thetac/2))+np.absolute(np.tan(thetad/2))))
            # Mode Shape
            for i in range(LDATA):
                shape_mode[i]=((2*np.pi*np.mean(fn_mode))**2)*np.mean(eta_mode)*2*r_mode[i]*np.sign(xc_mode[i])
                
            # Normalize
            shape_mode = shape_mode/np.linalg.norm(shape_mode, ord=np.inf) 
                
            # Show results
            plt.figure()
            plt.plot(shape_mode,'kx')
            plt.show()
            
            print([np.mean(fn_mode),np.mean(eta_mode)])
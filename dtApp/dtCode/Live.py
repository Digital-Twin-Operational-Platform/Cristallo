'''
This tool is for the reading of live sensor data
'''
from flask import render_template, request, redirect, url_for
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


@app.route('/live',methods=['GET','POST'])
def Monitor():
    if request.method=='GET': # Initial load
        sample=10e3  # Hz
        time0=1.0   #Seconds
        
        fig = make_subplots(rows=2, cols=2)
        plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template("live.html",rate=sample,Dur=time0,plot=plot)
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
            
            fig.update_layout(title_text="Bounds on displacement Frequency Response Function (FRF)",\
            showlegend=True,\
            font=dict(size=14),\
            plot_bgcolor= 'rgba(0, 0, 0, 0.1)',paper_bgcolor= 'rgba(0, 0, 0, 0)') #paper_bgcolor= 'rgba(0, 0, 0, 0.05)'
                        
            sideplot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            ActualSamplerate=1/((time0[15]-time0[0])/15)
            #%% Stop the scope
            # handle = chandle
            status["stop"] = ps.ps4000aStop(chandle)
            assert_pico_ok(status["stop"])
            
            # Disconnect the scope
            # handle = chandle
            status["close"] = ps.ps4000aCloseUnit(chandle)
            assert_pico_ok(status["close"])
                    
        
        return render_template('live.html', rate=ActualSamplerate,Dur=time0,plot=sideplot)
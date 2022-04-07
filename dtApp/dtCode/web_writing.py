# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 11:06:20 2022

@author: lab
"""

#%%Variables
SamplerateIntake=8000 #Hz
BuffertimeIntake=1 #S
Nbuffers=1   #kns

Samplerate=SamplerateIntake/1e6   #convert to microseconds #Hz samples/s(<1) Default=0.04
Buffertime=BuffertimeIntake*1e6 #convert to microseconds(us)/buffer   （>125)
SampleInterval=int(1/(Samplerate)*1e6) #convert to ps
Sizebuffer=int(Buffertime*Samplerate)
Sleeptime=0
mark_w = 1
c=1
while mark_w <2 :
    
    if c<9:
         #%% Pico set up
        import ctypes
        import numpy as np
        from picosdk.ps4000a import ps4000a as ps
        import matplotlib.pyplot as plt
        from picosdk.functions import adc2mV, assert_pico_ok
        import time
        
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
        disabled = 0
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
            
            # Set data buffer location for data collection from channel D
        
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
            
            print("Capturing at sample interval %s ns" % actualSampleIntervalNs)
            
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
            # handle = chandle
            # pointer to value = ctypes.byref(maxADC)
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
            ActualSamplerate=1/((time0[15]-time0[0])/15)
    
        
        #%%
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine=create_engine("postgresql+psycopg2://postgres:d1g1tw1n@localhost:5432",echo=True)
        Session = sessionmaker(bind=engine)
        session=Session()  
        
        from sqlalchemy import Column, Integer, String, ARRAY, Float, select
        from sqlalchemy.ext.declarative import declarative_base
        
        Base=declarative_base()
        
        class try1(Base):
            __tablename__='try1'
            
            id = Column(Integer(),primary_key=True)
            Time = Column(ARRAY(Float()))
            Channala = Column(ARRAY(Float()))
            Channalb = Column(ARRAY(Float()))
            Channalc = Column(ARRAY(Float()))
            Channald = Column(ARRAY(Float()))
            Buffersize = Column(String(255))
            SampleInterval = Column(String(255))
            ActualSamplerate = Column(String(255))
        
        
            
        
        Base.metadata.create_all(engine)
        
        
        # for i in range (1,9):
        #     livei=try1(id=i)
        #     session.add(livei)
        #     session.commit()
            
        session.query(try1).\
            filter(try1.id == c).\
            update({'Time': time0,'Channala': adc2mVChAMax[:],'Channalb':adc2mVChBMax[:],'Channalc':adc2mVChCMax[:],'Channald':adc2mVChDMax[:],'Buffersize':Sizebuffer,'SampleInterval':SampleInterval,'ActualSamplerate':ActualSamplerate})
        session.commit()
        
        session.close()
        
        # for i in range(len(time0)):
        #     ins = users.insert().values(
        #         time=time0[i],
        #         channala=adc2mVChAMax[:][i],
        #         channalb=adc2mVChBMax[:][i],
        #         channalc=adc2mVChCMax[:][i],
        #         channald=adc2mVChDMax[:][i],
        #         buffersize=Sizebuffer,
        #         #samplerate=,
        #         actualsamplerate=ActualSamplerate,    
        #     )
        #     print(str(ins))
            
        #%% Stop the scope
        # handle = chandle
        status["stop"] = ps.ps4000aStop(chandle)
        assert_pico_ok(status["stop"])
        
        # Disconnect the scope
        # handle = chandle
        status["close"] = ps.ps4000aCloseUnit(chandle)
        assert_pico_ok(status["close"])
        
        # Display status returns
        print(status)
        c += 1
        time.sleep(1)
    else: 
     c=1
     #%% Pico set up
    import ctypes
    import numpy as np
    from picosdk.ps4000a import ps4000a as ps
    import matplotlib.pyplot as plt
    from picosdk.functions import adc2mV, assert_pico_ok
    import time
    
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
    disabled = 0
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
        
        # Set data buffer location for data collection from channel D
    
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
        
        print("Capturing at sample interval %s ns" % actualSampleIntervalNs)
        
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
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
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
        ActualSamplerate=1/((time0[15]-time0[0])/15)

    
    #%%
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine=create_engine("postgresql+psycopg2://postgres:d1g1tw1n@localhost:5432",echo=True)
    Session = sessionmaker(bind=engine)
    session=Session()  
    
    from sqlalchemy import Column, Integer, String, ARRAY, Float, select
    from sqlalchemy.ext.declarative import declarative_base
    
    Base=declarative_base()
    
    class try1(Base):
        __tablename__='try1'
        
        id = Column(Integer(),primary_key=True)
        Time = Column(ARRAY(Float()))
        Channala = Column(ARRAY(Float()))
        Channalb = Column(ARRAY(Float()))
        Channalc = Column(ARRAY(Float()))
        Channald = Column(ARRAY(Float()))
        Buffersize = Column(String(255))
        SampleInterval = Column(String(255))
        ActualSamplerate = Column(String(255))
    
    
        
    
    Base.metadata.create_all(engine)
    
    
    # for i in range (1,9):
    #     livei=try1(id=i)
    #     session.add(livei)
    #     session.commit()
        
    session.query(try1).\
        filter(try1.id == c).\
        update({'Time': time0,'Channala': adc2mVChAMax[:],'Channalb':adc2mVChBMax[:],'Channalc':adc2mVChCMax[:],'Channald':adc2mVChDMax[:],'Buffersize':Sizebuffer,'SampleInterval':SampleInterval,'ActualSamplerate':ActualSamplerate})
    session.commit()
    
    session.close()
    
    # for i in range(len(time0)):
    #     ins = users.insert().values(
    #         time=time0[i],
    #         channala=adc2mVChAMax[:][i],
    #         channalb=adc2mVChBMax[:][i],
    #         channalc=adc2mVChCMax[:][i],
    #         channald=adc2mVChDMax[:][i],
    #         buffersize=Sizebuffer,
    #         #samplerate=,
    #         actualsamplerate=ActualSamplerate,    
    #     )
    #     print(str(ins))
        
    #%% Stop the scope
    # handle = chandle
    status["stop"] = ps.ps4000aStop(chandle)
    assert_pico_ok(status["stop"])
    
    # Disconnect the scope
    # handle = chandle
    status["close"] = ps.ps4000aCloseUnit(chandle)
    assert_pico_ok(status["close"])
    
    # Display status returns
    print(status)
    c += 1
    time.sleep(1)
'''
This function compares the experimental data of each structure with the simulation results of their respective numerical model.
'''
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import pandas as pd
import json

dataSwExp = pd.read_csv('dtLib/crossval/Data/Experimental Data/ExpDataSw.csv',header=None,sep=",")
dataShExp = pd.read_csv('dtLib/crossval/Data/Experimental Data/ExpDataSh.csv',header=None,sep=",")
dataSoExp = pd.read_csv('dtLib/crossval/Data/Experimental Data/ExpDataSo.csv',header=None,sep=",")
dataBrExp = pd.read_csv('dtLib/crossval/Data/Experimental Data/ExpDataBr.csv',header=None,sep=",")

dataSwNum = pd.read_csv('dtLib/crossval/Data/Numerical Data/NumDataSw.csv',header=None,sep=",")
dataShNum = pd.read_csv('dtLib/crossval/Data/Numerical Data/NumDataSh.csv',header=None,sep=",")
dataSoNum = pd.read_csv('dtLib/crossval/Data/Numerical Data/NumDataSo.csv',header=None,sep=",")
dataBrNum = pd.read_csv('dtLib/crossval/Data/Numerical Data/NumDataBr.csv',header=None,sep=",")

LimitsExp = np.array([0,322,6561,1313,80002]) #0/Sw/Sh/So/Br
LimitsNum = np.array([0,3998,3998,3992,400]) #0/Sw/Sh/So/Br

################################ Experimental Data ######################
tSW=dataSwExp.iloc[LimitsExp[0]:LimitsExp[1],0]
youtSW = [dataSwExp.iloc[LimitsExp[0]:LimitsExp[1],1],dataSwExp.iloc[LimitsExp[0]:LimitsExp[1],2],dataSwExp.iloc[LimitsExp[0]:LimitsExp[1],3]]

tSH=dataShExp.iloc[LimitsExp[0]:LimitsExp[2],0]
youtSH = [dataShExp.iloc[LimitsExp[0]:LimitsExp[2],1],dataShExp.iloc[LimitsExp[0]:LimitsExp[2],2],dataShExp.iloc[LimitsExp[0]:LimitsExp[2],3]]

tSO=dataSoExp.iloc[LimitsExp[0]:LimitsExp[3],0]
youtSO = [dataSoExp.iloc[LimitsExp[0]:LimitsExp[3],1],dataSoExp.iloc[LimitsExp[0]:LimitsExp[3],2],dataSoExp.iloc[LimitsExp[0]:LimitsExp[3],3]]

tBR=dataBrExp.iloc[LimitsExp[0]:LimitsExp[4],0]
youtBR = [dataBrExp.iloc[LimitsExp[0]:LimitsExp[4],1],dataBrExp.iloc[LimitsExp[0]:LimitsExp[4],2],dataBrExp.iloc[LimitsExp[0]:LimitsExp[4],3]]
################################ Numerical Data ######################
tNumSW=dataSwNum.iloc[LimitsNum[0]:LimitsNum[1],0]
tNumSWmiddle=dataSwNum.iloc[LimitsNum[0]:LimitsNum[1],1]
youtNumSW = [dataSwNum.iloc[LimitsNum[0]:LimitsNum[1],2],dataSwNum.iloc[LimitsNum[0]:LimitsNum[1],3],dataSwNum.iloc[LimitsNum[0]:LimitsNum[1],4]]

tNumSH=dataShNum.iloc[LimitsNum[0]:LimitsNum[2],0]
tNumSHmiddle=dataShNum.iloc[LimitsNum[0]:LimitsNum[2],1]
youtNumSH = [dataShNum.iloc[LimitsNum[0]:LimitsNum[2],2],dataShNum.iloc[LimitsNum[0]:LimitsNum[2],3],dataShNum.iloc[LimitsNum[0]:LimitsNum[2],4]]

tNumSO=dataSoNum.iloc[LimitsNum[0]:LimitsNum[3],0]
youtNumSO = [dataSoNum.iloc[LimitsNum[0]:LimitsNum[3],1],dataSoNum.iloc[LimitsNum[0]:LimitsNum[3],2],dataSoNum.iloc[LimitsNum[0]:LimitsNum[3],3]]

tNumBR=dataBrNum.iloc[LimitsNum[0]:LimitsNum[4],0]
youtNumBR = [dataBrNum.iloc[LimitsNum[0]:LimitsNum[4],1],dataBrNum.iloc[LimitsNum[0]:LimitsNum[4],2],dataBrNum.iloc[LimitsNum[0]:LimitsNum[4],3]]


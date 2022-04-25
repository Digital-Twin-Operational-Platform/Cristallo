'''
This function extracts the experimental and simulated data.
'''
import numpy as np
from typing import Generator

from .data_location import data_location

def readfile_gen(fullpath,sep=','):
    with open(fullpath,"r") as f:
        for row in f: yield row.split(sep)

def slice_data(x:Generator,istart:int,iend:int):
    x_=iter(x)
    X=[]
    i=0
    while True:
        try: xi = next(x_)
        except: break
        if (istart<=i) & (i<=iend): X.append(xi)
        i+=1
    return np.asarray(X,dtype=float)

def extract_data(fullpath,istart:int=0,iend:int=10_000): 
    return slice_data(readfile_gen(fullpath),istart=istart,iend=iend)

LimitsExp = np.array([0,322,6561,1313,80002]) #0/Sw/Sh/So/Br
LimitsNum = np.array([0,3998,3998,3992,400]) #0/Sw/Sh/So/Br

dataSwExp = extract_data(data_location['experimental']['Swansea']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[1])
tSW = dataSwExp[:,0]
youtSW = dataSwExp[:,1:4]

dataShExp = extract_data(data_location['experimental']['Sheffield']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[2])
tSH = dataShExp[:,0]
youtSH = dataShExp[:,1:4]

dataSoExp = extract_data(data_location['experimental']['Southampton']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[3])
tSO = dataSoExp[:,0]
youtSO = dataSoExp[:,1:4]

dataBrExp = extract_data(data_location['experimental']['Bristol']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[4])
tBR = dataBrExp[:,0]
youtBR = dataBrExp[:,1:4]


dataSwNum = extract_data(data_location['simulated']['Swansea']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[1])
tNumSW = dataSwNum[:,0]
tNumSWmiddle = dataSwNum[:,1]
youtNumSW = dataSwNum[:,2:]

dataShNum = extract_data(data_location['simulated']['Sheffield']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[2])
tNumSH = dataShNum[:,0]
tNumSHmiddle = dataShNum[:,1]
youtNumSH = dataShNum[:,2:]

dataSoNum = extract_data(data_location['simulated']['Southampton']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[3])
tNumSO = dataSoNum[:,0]
tNumSOmiddle = dataSoNum[:,1]
youtNumSO = dataSoNum[:,1:4]

dataBrNum = extract_data(data_location['simulated']['Bristol']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[4])
tNumBR = dataBrNum[:,0]
tNumBRmiddle = dataBrNum[:,1]
youtNumBR = dataBrNum[:,1:4]


# dataSwExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSw.csv')
# dataShExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSh.csv')
# dataSoExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSo.csv')
# dataBrExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataBr.csv')

# dataSwNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSw.csv')
# dataShNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSh.csv')
# dataSoNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSo.csv')
# dataBrNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataBr.csv')

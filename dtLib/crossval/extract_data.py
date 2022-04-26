'''
This function extracts the experimental and simulated data.
'''
import numpy as np
from typing import Generator

from .data_location import data_particulars

def readfile_gen(fullpath,sep=','):
    with open(fullpath,"r") as f:
        for row in f: yield row.split(sep)

def slice_data(x:Generator,istart:int,iend:int):
    x_=iter(x)
    X=[]
    X_append = X.append
    i=0
    while True:
        try: xi = next(x_)
        except StopIteration: break
        if (istart<=i) & (i<=iend): X_append(xi)
        i+=1
    return np.asarray(X,dtype=float)

def extract_data(fullpath,istart:int=0,iend:int=10_000): 
    return slice_data(readfile_gen(fullpath),istart=istart,iend=iend)

# LimitsExp = np.array([0,322,6561,1313,80002]) #0/Sw/Sh/So/Br
# LimitsNum = np.array([0,3998,3998,3992,400]) #0/Sw/Sh/So/Br

################################ Experimental Data ######################
limits_sw_exp = data_particulars['experimental']['Swansea']['slice_range']
path_sw_exp = data_particulars['experimental']['Swansea']['fullpath']
data_sw_exp = extract_data(path_sw_exp,istart=limits_sw_exp[0],iend=limits_sw_exp[1]) # dataSwExp = extract_data(data_particulars['experimental']['Swansea']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[1])
tSW = data_sw_exp[:,0] # KEEP VARIABLE NAME
youtSW = data_sw_exp[:,1:4] # KEEP VARIABLE NAME

limits_sh_exp = data_particulars['experimental']['Sheffield']['slice_range']
path_sh_exp = data_particulars['experimental']['Sheffield']['fullpath']
data_sh_exp = extract_data(path_sh_exp,istart=limits_sh_exp[0],iend=limits_sh_exp[1]) # dataShExp = extract_data(data_particulars['experimental']['Sheffield']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[2])
tSH = data_sh_exp[:,0] # KEEP VARIABLE NAME
youtSH = data_sh_exp[:,1:4] # KEEP VARIABLE NAME

limits_so_exp = data_particulars['experimental']['Southampton']['slice_range']
path_so_exp = data_particulars['experimental']['Southampton']['fullpath']
data_so_exp = extract_data(path_so_exp,istart=limits_so_exp[0],iend=limits_so_exp[1]) # dataSoExp = extract_data(data_particulars['experimental']['Southampton']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[3])
tSO = data_so_exp[:,0] # KEEP VARIABLE NAME
youtSO = data_so_exp[:,1:4] # KEEP VARIABLE NAME

limits_br_exp = data_particulars['experimental']['Bristol']['slice_range']
path_br_exp = data_particulars['experimental']['Bristol']['fullpath']
data_br_exp = extract_data(path_br_exp,istart=limits_br_exp[0],iend=limits_br_exp[1]) # dataBrExp = extract_data(data_particulars['experimental']['Bristol']['fullpath'],istart=LimitsExp[0],iend=LimitsExp[4])
tBR = data_br_exp[:,0] # KEEP VARIABLE NAME
youtBR = data_br_exp[:,1:4] # KEEP VARIABLE NAME

################################ Simulated Data ######################
limits_sw_num = data_particulars['simulated']['Swansea']['slice_range']
path_sw_num = data_particulars['simulated']['Swansea']['fullpath']
data_sw_num = extract_data(path_sw_num,istart=limits_sw_num[0],iend=limits_sw_num[1]) # dataSwNum = extract_data(data_particulars['simulated']['Swansea']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[1])
tNumSW = data_sw_num[:,0] # KEEP VARIABLE NAME
tNumSWmiddle = data_sw_num[:,1] 
youtNumSW = data_sw_num[:,2:] # KEEP VARIABLE NAME

limits_sh_num = data_particulars['simulated']['Sheffield']['slice_range']
path_sh_num = data_particulars['simulated']['Sheffield']['fullpath']
data_sh_num = extract_data(path_sh_num,istart=limits_sh_num[0],iend=limits_sh_num[1]) # dataShNum = extract_data(data_particulars['simulated']['Sheffield']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[2])
tNumSH = data_sh_num[:,0] # KEEP VARIABLE NAME
tNumSHmiddle = data_sh_num[:,1]
youtNumSH = data_sh_num[:,2:] # KEEP VARIABLE NAME

limits_so_num = data_particulars['simulated']['Southampton']['slice_range']
path_so_num = data_particulars['simulated']['Southampton']['fullpath']
data_so_num = extract_data(path_so_num,istart=limits_so_num[0],iend=limits_so_num[1])# dataSoNum = extract_data(data_particulars['simulated']['Southampton']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[3])
tNumSO = data_so_num[:,0] # KEEP VARIABLE NAME
tNumSOmiddle = data_so_num[:,1]
youtNumSO = data_so_num[:,1:4] # KEEP VARIABLE NAME

limits_br_num = data_particulars['simulated']['Southampton']['slice_range']
path_br_num = data_particulars['simulated']['Southampton']['fullpath']
data_br_num = extract_data(path_br_num,istart=limits_br_num[0],iend=limits_br_num[1]) # dataBrNum = extract_data(data_particulars['simulated']['Bristol']['fullpath'],istart=LimitsNum[0],iend=LimitsNum[4])
tNumBR = data_br_num[:,0] # KEEP VARIABLE NAME
tNumBRmiddle = data_br_num[:,1]
youtNumBR = data_br_num[:,1:4] # KEEP VARIABLE NAME


# dataSwExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSw.csv')
# dataShExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSh.csv')
# dataSoExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSo.csv')
# dataBrExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataBr.csv')

# dataSwNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSw.csv')
# dataShNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSh.csv')
# dataSoNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSo.csv')
# dataBrNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataBr.csv')

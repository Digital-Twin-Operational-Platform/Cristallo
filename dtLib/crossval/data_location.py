data_particulars = {
    'experimental':{
        'Swansea':{
            'fullpath':'dtLib/crossval/Data/Experimental Data/ExpDataSw.csv',
            'slice_range':[0,322],
            },
        'Sheffield':{
            'fullpath':'dtLib/crossval/Data/Experimental Data/ExpDataSh.csv',
            'slice_range':[0,6561],
            },
        'Southampton':{
            'fullpath':'dtLib/crossval/Data/Experimental Data/ExpDataSo.csv',
            'slice_range':[0,1313],
            },
        'Bristol':{
            'fullpath':'dtLib/crossval/Data/Experimental Data/ExpDataBr.csv',
            'slice_range':[0,80002],
            },
    },
    'simulated':{
        'Swansea':{
            'fullpath':'dtLib/crossval/Data/Numerical Data/NumDataSw.csv',
            'slice_range':[0,3998],
            },
        'Sheffield':{
            'fullpath':'dtLib/crossval/Data/Numerical Data/NumDataSh.csv',
            'slice_range':[0,3998],
            },
        'Southampton':{
            'fullpath':'dtLib/crossval/Data/Numerical Data/NumDataSo.csv',
            'slice_range':[0,3992],
            },
        'Bristol':{
            'fullpath':'dtLib/crossval/Data/Numerical Data/NumDataBr.csv',
            'slice_range':[0,400],
            },
    }
}

# LimitsExp = np.array([0,322,6561,1313,80002]) #0/Sw/Sh/So/Br
# LimitsNum = np.array([0,3998,3998,3992,400]) #0/Sw/Sh/So/Br

# dataSwExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSw.csv')
# dataShExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSh.csv')
# dataSoExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataSo.csv')
# dataBrExp = readfile_gen('dtLib/crossval/Data/Experimental Data/ExpDataBr.csv')

# dataSwNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSw.csv')
# dataShNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSh.csv')
# dataSoNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataSo.csv')
# dataBrNum = readfile_gen('dtLib/crossval/Data/Numerical Data/NumDataBr.csv')

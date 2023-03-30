import os
data_particulars = {
    'experimental':{
        'Swansea':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Experimental Data","ExpDataSw.csv"),
            'slice_range':[0,322],
            },
        'Sheffield':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Experimental Data","ExpDataSh.csv"),
            'slice_range':[0,6561],
            },
        'Southampton':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Experimental Data","ExpDataSo.csv"),
            'slice_range':[0,1313],
            },
        'Bristol':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Experimental Data","ExpDataBr.csv"),
            'slice_range':[0,80002],
            },
    },
    'simulated':{
        'Swansea':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Numerical Data","NumDataSw.csv"),
            'slice_range':[0,3998],
            },
        'Sheffield':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Numerical Data","NumDataSh.csv"),
            'slice_range':[0,3998],
            },
        'Southampton':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Numerical Data","NumDataSo.csv"),
            'slice_range':[0,3992],
            },
        'Bristol':{
            'fullpath':os.path.join("digitaltwin","dtLib","crossval","Data","Numerical Data","NumDataBr.csv"),
            'slice_range':[0,400],
            },
    }
}

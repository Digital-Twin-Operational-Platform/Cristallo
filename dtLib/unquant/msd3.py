'''

`dtLib/msd3.py`


:Author: 
    Marco De Angelis

:Organisation: 
    University of Liverpool

:Copyright: 
    BSD Licence


This single python file ``msd3.py`` is the scientific code for the uncertainty page.

This module is intended to be self-contained, thus it is orthogonal to any other module in this software. 


The code in this file is inspired by functional programming. 

    Sometimes the elegant implementation is a function. Not a method. Not a class. Not a framework. Just a function.
    -- John Carmack.


If inputs are not passed to the functions of this module the following values will be assumed:

.. code-block:: python

    MASS = [5.362, 5.144,  5.142]            # *1e4 kg

    STFF = [3.846, 4.464, 4.589]             # *1e8 N/m

    DAMP = [1.699, 1.016, 1.34]              # *1e4 Ns/m

    NN = 300 # number of frequencies for the FRF plot

    W_RANGE = [5,200] # frequency range for plotting
    
    WW = 62.832 # A frequency
    
    EXCI_FLOOR = '3'


This page makes use of the following dependencies.

External dependencies 

.. code-block:: python

    import numpy
    import numpy.linalg as LA


If not otherwise specified: 

|    * The excitation is applied at floor 3. 
|    * The frequency range is [5,200] Hz.
|    * The FRF plots 300 frequencies.
|    * The number of MonteCarlo samples is 50.
'''


import numpy
import numpy.linalg as LA

# import matplotlib.pyplot as pyplot

# Global values for the system parameters
MM = [5.362*1e4, 5.144*1e4,  5.142*1e4]            # *1e4
KK = [3.846*1e8, 4.464*1e8, 4.589*1e8]             # *1e8
CC = [1.699*1e4, 1.016*1e4, 1.34*1e4]              # *1e4

MM_Interval = [[5*1e4,6*1e4],[5*1e4,6*1e4],[5*1e4,6*1e4]]        # *1e4
KK_Interval = [[3*1e8,4*1e8],[4*1e8,5*1e8],[4*1e8,5*1e8]]        # *1e8
CC_Interval = [[1*1e4,2*1e4],[1*1e4,2*1e4],[1*1e4,2*1e4]]        # *1e4

# O†her global parameters
NN = 300 # number of frequencies for the FRF plot
W_RANGE = [5,200] # frequency range for plotting
WW = 62.832 # A frequency
EXCI_FLOOR = '3'

def input_parser(m=None,k=None,c=None):
    if m is None:
        m1,m2,m3 = MM[0], MM[1], MM[2]
    else:
        m1,m2,m3 = m[0], m[1], m[2]
    if c is None:
        c1,c2,c3 = CC[0], CC[1], CC[2]
    else:
        c1,c2,c3 = c[0], c[1], c[2]
    if k is None:
        k1,k2,k3 = KK[0], KK[1], KK[2]
    else:
        k1,k2,k3 = k[0], k[1], k[2]
    return m1,m2,m3,k1,k2,k3,c1,c2,c3

def input_morphism(w=None, nn=None, w_range=None, exci_floor=None):
    if w is None:
        w = WW
    if nn is None:
        nn = NN
    if w_range is None:
        w_range = W_RANGE
    if exci_floor is None:
        exci_floor=EXCI_FLOOR
    return w,nn,w_range,exci_floor

def input_parser_interval(mI=None,kI=None,cI=None):
    '''
    Function description.

    :param mI:   Interval vector 1x3 (floats) for the mass
    :param kI:   Interval vector 1x3 (floats) for the stiffness 
    :param cI:   Interval vector 1x3 (floats) for the damping 

    :returns: interval vector 1x3 of mass, stiffness and damping 
    '''
    if mI is None:
        mI = interval_iterable_silent(MM_Interval) # returns itself if the correct structure is passed, else returns None (or error)
    if cI is None:
        cI = interval_iterable_silent(CC_Interval)
    if kI is None:
        kI = interval_iterable_silent(KK_Interval)
    return mI,kI,cI

def M_K_C(m=None,k=None,c=None):
    '''
    This function returns the mass, stifness and damping matrices.

    :param m:   Mass vector 1x3 (floats)
    :param k:   Stiffness vector 1x3 (floats)
    :param c:   Damping vector 1x3 (floats)

    :returns: values of mass, stiffness and damping 
    '''
    m1,m2,m3,k1,k2,k3,c1,c2,c3 = input_parser(m,k,c)
    K = [[k1+k2 ,-k2    , 0  ],
         [-k2   , k2+k3 , -k3],
         [ 0    ,-k3    , k3 ]]
    C = [[c1+c2 ,-c2    , 0  ],
         [-c2   , c2+c3 , -c3],
         [ 0    ,-c3    , c3 ]]
    M = [[m1    ,0      ,0  ],
         [0     ,m2     ,0  ],
         [0     ,0      ,m3 ]]
    return M,K,C

def system_matrix(w=None,m=None,k=None,c=None):
    w,_,_,_ = input_morphism(w=w)
    M,K,C = M_K_C(m=m,k=k,c=c)
    D = []
    for i in range(3):
        d = []
        for j in range(3):
            d.append(-w**2*M[i][j] + 1j*w*C[i][j] + K[i][j])
        D.append(d)
    return D

def displacement_msd_numpy(w=None,m=None,k=None,c=None,exci_floor=None):
    w,_,_,exci_floor = input_morphism(w=w,exci_floor=exci_floor)
    D = system_matrix(w=w,m=m,k=k,c=c)
    D_arr = numpy.array(D)
    invD = numpy.linalg.inv(D_arr)
    if exci_floor=='3': # excitation at floor 3 and so on
        exci = numpy.array([0,0,1])
    elif exci_floor=='2':
        exci = numpy.array([0,1,0])
    elif exci_floor=='1':
        exci = numpy.array([1,0,0])
    u = invD@exci
    return u

def displacement_msd_numpy_abs(w=None,m=None,k=None,c=None,exci_floor=None):
    w,_,_,exci_floor = input_morphism(w=w,exci_floor=exci_floor)
    return abs(displacement_msd_numpy(w=w,m=m,k=k,c=c,exci_floor=exci_floor))

def displacement_msd_numpy_abs_ww(w_range=None,m=None,k=None,c=None,n=None,exci_floor=None):
    _,n,w_range,exci_floor = input_morphism(nn=n,w_range=w_range,exci_floor=exci_floor)
    ww = numpy.linspace(w_range[0],w_range[1],n)
    U=[]
    for w in ww:
        U.append(displacement_msd_numpy_abs(w=w,m=m,k=k,c=c,exci_floor=exci_floor))
    return ww,U

def displacement_bounds_cartesian_MK(w_range=None,mI=None,kI=None,cI=None,n1=None,n2=30,exci_floor=None):
    '''
    Computes the bounds of the FRF with a Cartesian grid search. 

    :param w_range:   Range of frequencies to be considered
    :param mI:   Interval vector 1x3 (floats) for the mass
    :param kI:   Interval vector 1x3 (floats) for the stiffness 
    :param cI:   Interval vector 1x3 (floats) for the damping 
    :param n1:   Number of frequencies, if ``None`` uses default value
    :param n2:   Dimension of the grid, total number of points is ``n2**2``
    :param exci_floor: Floor at which excitation is applied (int)

    :returns: Bounds on the absolute value of the displacement (FRF bounds)
    '''
    _,n1,w_range,exci_floor = input_morphism(nn=n1,w_range=w_range,exci_floor=exci_floor)
    mI,kI,cI = input_parser_interval(mI,kI,cI)
    m_linspace = list(numpy.array([numpy.linspace(lo(m),hi(m),num=n2) for m in mI]).T)
    k_linspace = list(numpy.array([numpy.linspace(lo(k),hi(k),num=n2) for k in kI]).T)
    ww=list(numpy.linspace(w_range[0],w_range[1],num=n1))
    YY=[]
    for w in ww:
        YHI=[]
        YLO=[]
        for mi in m_linspace:
            for ki in k_linspace:
                YHI.append(displacement_msd_numpy_abs(w=w,m=mi,k=ki,c=lo(cI),exci_floor=exci_floor))
                YLO.append(displacement_msd_numpy_abs(w=w,m=mi,k=ki,c=hi(cI),exci_floor=exci_floor))
        YY.append(numpy.array([numpy.min(YLO+YHI,axis=0),numpy.max(YLO+YHI,axis=0)]).T)
    return ww,YY

def displacement_bounds_montecarlo(w_range=None,mI=None,kI=None,cI=None,n1=None,n2=30,exci_floor=None):
    '''
    Computes the bounds of the FRF using a brute-force Monte Carlo method.

    :param w_range:   Range of frequencies to be considered
    :param mI:   Interval vector 1x3 (floats) for the mass
    :param kI:   Interval vector 1x3 (floats) for the stiffness 
    :param cI:   Interval vector 1x3 (floats) for the damping 
    :param n1:   Number of frequencies, if ``None`` uses default value
    :param n2:   Dimension of the grid, total number of points is ``n2**2``
    :param exci_floor: Floor at which excitation is applied (int)

    :returns: Inner bounds on the absolute value of the displacement (FRF bounds)
    '''
    _,n1,w_range,exci_floor = input_morphism(nn=n1,w_range=w_range,exci_floor=exci_floor)
    mI,kI,cI = input_parser_interval(mI,kI,cI)
    ww = numpy.linspace(w_range[0],w_range[1],num=n1)
    YY= []
    for w in ww:
        t_min,t_MAX = [float('inf') for _ in range(3)], [-float('inf') for _ in range(3)]
        for _ in range(n2):
            m_r = rand(mI)
            k_r = rand(kI)
            c_r = rand(cI)
            abs_disp3 = displacement_msd_numpy_abs(w=w,m=m_r,k=k_r,c=c_r,exci_floor=exci_floor)
            for i,o in enumerate(abs_disp3):
                if o < t_min[i]:
                    t_min[i] = o
                if o > t_MAX[i]:
                    t_MAX[i] = o
        YY.append([[tm,tM] for tm,tM in zip(t_min,t_MAX)])
    return ww,YY

def displacement_bounds_subintervalization(w_range=None,mI=None,kI=None,cI=None,n1=None,n2=30,exci_floor=None):
    pass

# Some handy functions
def is_iterable(x):
    try:
        for _ in x:
            break
    except TypeError as err:
        return False # print("{0}".format(err))
    return True
def is_interval_iterable(x): 
    if is_iterable(x):
        for xi in x:
            if is_iterable(xi):
                if len(xi) != 2:
                    return False
                elif xi[1] < xi[0]:
                    return False
                return True # It qualifies as an interval array/vector
    return False
def is_interval_object(x):
    if len(x) == 2:
        if x[0] <= x[1]: 
            return True # It qualifies as an interval object. Note: interval objects can be vectors but should not behave as interval iterables.
    return False
def interval_iterable_silent(x): # returns itself if interval iterable
    if is_interval_iterable(x):
        return x
    pass
def interval_object_silent(x): # returns itself if interval object
    if is_interval_object(x):
        return x
    pass
def lo(x): 
    '''
    If x qualifies, this returns the left endpoints collected in a list.

    :param x: An iterable of intervals or an interval object

    :returns: a list of left endpoints or a single left endpoint
    '''
    if is_interval_iterable(x):
        return [xi[0] for xi in x]
    elif is_interval_object(x):
        return x[0]
    pass #         raise TypeError('Cant take the left endpoint. It does not qulify as interval array.')   
def hi(x): 
    '''
    If x qualifies, this returns the right endpoints collected in a list.

    :param x: An iterable of intervals or an interval object

    :returns: a list of right endpoints or a single right endpoint
    '''
    if is_interval_iterable(x):
        return [xi[1] for xi in x]
    elif is_interval_object(x):
        return x[1]
    pass #         raise TypeError('Cant take the right endpoint. It does not qulify as interval array.')   
def rand(x): # if x qualifies, this returns a random inner point
    if is_interval_iterable(x):
        dim = len(x)
        r = numpy.random.random_sample(size=dim)
        return [xi[0] + ri*(xi[1]-xi[0]) for xi,ri in zip(x,r)]
    elif is_interval_object(x):
        r = numpy.random.random_sample()
        return x[0] + r*(x[1]-x[0])
    pass
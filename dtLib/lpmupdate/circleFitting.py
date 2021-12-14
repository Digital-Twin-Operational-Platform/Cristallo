from numpy import *
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



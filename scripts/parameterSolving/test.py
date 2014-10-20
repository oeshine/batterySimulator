# -*- coding: utf-8 -*-
from lmfit import minimize, Parameters, Parameter, report_fit
import numpy as np
x = np.array([0.009,0.014,0.03,0.046,0.062,0.078,0.094,0.11\
          ,0.125,0.141,0.157,0.173,0.189,0.205,0.221,0.237\
          ,0.253,0.269,0.284,0.3,0.316,0.332,0.348,0.364\
          ,0.38,0.396,0.412,0.428,0.443,0.459,0.475,0.491\
          ,0.507,0.523,0.539,0.555,0.571,0.587,0.602,0.618\
          ,0.634,0.65,0.666,0.682,0.698,0.714,0.73,0.746,0.761\
          ,0.777,0.793,0.809,0.825,0.841,0.857,0.873,0.889\
          ,0.905,0.92,0.936,0.952,0.968,0.984,0.99])
data = np.array([2.80,3.023,3.159,3.25,3.318,3.362,3.383,3.398,3.412,3.429,3.446\
              ,3.462,3.477,3.49,3.503,3.513,3.524,3.535,3.545,3.557,3.569\
              ,3.584,3.594,3.601,3.607,3.612,3.618,3.624,3.629,3.635,3.642\
              ,3.648,3.656,3.664,3.672,3.682,3.693,3.706,3.721,3.74,3.761\
              ,3.78,3.797,3.813,3.829,3.846,3.861,3.877,3.893,3.909,3.926\
              ,3.943,3.96,3.978,3.997,4.017,4.037,4.057,4.077,4.096,4.115\
              ,4.135,4.158,4.184])
# define objective function: returns the array to be minimized
def fcn2min(params, x, data):
    """ model , subtract data"""
    K0 = params['K0'].value
    K1 = params['K1'].value
    K2 = params['K2'].value
    K3 = params['K3'].value
    K4 = params['K4'].value
    model = K0+K1*x-K2/x+K3*np.log(x)+K4*np.log(1-x)
    return model - data

# create a set of Parameters
params = Parameters()
params.add('K0', value= 3.7638)
params.add('K1', value= -0.00013)
params.add('K2', value= 0.3650)
params.add('K3', value= 0.2201)
params.add('K4', value= -0.0272)

# do fit, here with leastsq model
result = minimize(fcn2min, params, args=(x, data))

# calculate final result
final = data + result.residual

# write error report
report_fit(params)

print final
# try to plot results
try:
    import pylab
    pylab.plot(x, data, 'k+')
    pylab.plot(x, final, 'r')
    pylab.show()
except:
    pass
    




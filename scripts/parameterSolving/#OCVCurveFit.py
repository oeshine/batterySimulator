import numpy as np

#from pykalman import KalmanFilter
import pickle
from scipy import interpolate
import matplotlib.pylab as plt
import random
from scipy.optimize import leastsq


batteryTime=0
relayStatus=0
totalVoltage=0.0
totalCurrent=0.0
quitFlag=0
    
# chargeVoltage=np.array([3.023, 3.398, 3.490, 3.557, 3.618, 3.656, 3.721, 3.846, 3.943, 4.057, 4.184])
# chargeQuantity=np.array([74.2, 583, 1086.5, 1590.0, 2183.6, 2687.1, 3190.6, 3784.2, 4287.7, 4796.5, 5300.0])
# chargeSOC=np.array([0.014,0.11,0.205,0.30,0.412,0.507,0.602,0.714,0.809,0.905,1.0])

chargeQuantity=[10.0,74.2,159,243.8,328.6,413.4,498.2,583,662.5,747.3,832.1\
               ,916.9,1001.7,1086.5,1171.3,1256.1,1340.9,1425.7,1505.2\
               ,1590,1674.8,1759.6,1844.4,1929.2,2014,2098.8,2183.6,2268.4\
               ,2347.9,2432.7,2517.5,2602.3,2687.1,2771.9,2856.7,2941.5\
               ,3026.3,3111.1,3190.6,3275.4,3360.2,3445,3529.8,3614.6\
               ,3699.4,3784.2,3869,3953.8,4033.3,4118.1,4202.9,4287.7\
               ,4372.5,4457.3,4542.1,4626.9,4711.7,4796.5,4876,4960.8\
               ,5045.6,5130.4,5215.2,5300]
               
chargeVoltage=np.array([2.80,3.023,3.159,3.25,3.318,3.362,3.383,3.398,3.412,3.429,3.446\
              ,3.462,3.477,3.49,3.503,3.513,3.524,3.535,3.545,3.557,3.569\
              ,3.584,3.594,3.601,3.607,3.612,3.618,3.624,3.629,3.635,3.642\
              ,3.648,3.656,3.664,3.672,3.682,3.693,3.706,3.721,3.74,3.761\
              ,3.78,3.797,3.813,3.829,3.846,3.861,3.877,3.893,3.909,3.926\
              ,3.943,3.96,3.978,3.997,4.017,4.037,4.057,4.077,4.096,4.115\
              ,4.135,4.158,4.184])
              
chargeSOC=np.array([0.009,0.014,0.03,0.046,0.062,0.078,0.094,0.11\
          ,0.125,0.141,0.157,0.173,0.189,0.205,0.221,0.237\
          ,0.253,0.269,0.284,0.3,0.316,0.332,0.348,0.364\
          ,0.38,0.396,0.412,0.428,0.443,0.459,0.475,0.491\
          ,0.507,0.523,0.539,0.555,0.571,0.587,0.602,0.618\
          ,0.634,0.65,0.666,0.682,0.698,0.714,0.73,0.746,0.761\
          ,0.777,0.793,0.809,0.825,0.841,0.857,0.873,0.889\
          ,0.905,0.92,0.936,0.952,0.968,0.984,0.99])
                


    
def qvRealtion(voltage):
    global chargeVoltage, chargeQuantity
    vPoints=chargeVoltage
    qPoints=chargeQuantity
    #SOCPoints=chargeSOC
    qvCurveTck=interpolate.splrep(vPoints,qPoints,s=0.002)
    batteryQuantity=interpolate.splev(voltage,qvCurveTck,der=0)
    #SOCVCurveTck=interpolate.splrep(SOCPoints,vPoints,s=0.002)
    #batterySOC=interpolate.splev(voltage,SOCVCurveTck,der=0)
    #newX = np.arange(vPoints[0],vPoints[-1],0.1)
    # newY = interpolate.splev(newX,qvCurveTck,der=0)
    # plt.plot(vPoints,qPoints,'o',newX,newY,'-')
    # plt.title("V-Q curve")
    #newSOC=np.arange(SOCPoints[0],SOCPoints[-1],0.01)
    #newVoltage=interpolate.splev(newSOC,SOCVCurveTck,der=0)
    #plt.plot(SOCPoints,vPoints,'o',newSOC,newVoltage,'-')
    #plt.title("V-SOC curve")
    #plt.show()
    return batteryQuantity

#P0 =[ 3.346366    0.59163954 -0.00542907 -0.0092671  -0.06431112]
#real parameter[ 3.346366,0.59163954,0.00542907,-0.0092671,-0.06431112]  
def fun(Zk,P):
    K0,K1,K2,K3,K4=P
    return K0+K1*Zk+K2/Zk+K3*np.log(Zk)+K4*np.log(1-Zk)
    #return 3.7638--0.00013*ZK-0.3650/ZK+0.2201*np.log(ZK)-0.0272*np.log(1-ZK)
    

def residuals(P,Yk,Zk):
    err = Yk-fun(Zk,P)
    return err

def plotfun(P):
    x=chargeSOC
    fig= plt.figure()
    fig.suptitle('Real SOC_OCV Curve and Fit Curve',fontsize=14,fontweight='bold')
    ax = fig.add_subplot(1,1,1)
    ax.set_xlabel('SOC(%)')
    ax.set_ylabel('Voltage(V)')
    y = fun(x,P)
    ax.plot(x*100,y,'b--',label='Estimated Curve')
    ax.plot(chargeSOC*100,chargeVoltage,'g',label='Real Curve')
    ax2 = ax.twinx()
    s2=(chargeVoltage-y)*100
    ax2.set_ylim(-10,90)
    ax2.plot(chargeSOC*100, s2, 'r--',label='Error')
    ax2.set_ylabel('Error(%)', color='r')
    ax.legend(loc="upper left")
    ax2.legend(loc="lower right")
    plt.show()


def calSOC():
    f=open('calSOC.txt','a')
    initQuantity=[0]*NumberOfCells*NumberOfStacks
    initSOC=[0]*NumberOfCells*NumberOfStacks
    dischargeQuantity=[0]*NumberOfCells*NumberOfStacks
    SOC=[0]*NumberOfCells*NumberOfStacks
    batteryTime=int(sendCommand('J000')) #sync the clock by reading clock in the battery simulator
    f.write(str(batteryTime)+'\t')
    if batteryTime == 0:
        for index in range(len(voltage)):
            initQuantity[index]=qvRealtion(voltage[index])
            initSOC[index]=initQuantity[index]/BATTERYCAPACITY
        totalQuantity=sum(initQuantity)
        totalSOC=totalQuantity/(BATTERYCAPACITY*NumberOfCells*NumberOfStacks)
        f.write(str(totalSOC)+'\t')
        f.write('\n')
        f.close()
        pickle.dump(initQuantity,open('data.pickle','w'))        
    else:
        initialQuantity=pickle.load(open('data.pickle','r'))
        for index in range(len(initialQuantity)):
            dischargeQuantity[index]=initialQuantity[index]- totalCurrent * batteryTime/3600
            SOC[index]=dischargeQuantity[index]/BATTERYCAPACITY
        totalQuantity=sum(dischargeQuantity)
        totalSOC=totalQuantity/(BATTERYCAPACITY*NumberOfCells*NumberOfStacks)
        f.write(str(totalSOC)+'\t')
        f.write('\n')
        f.close()
        


if __name__ == '__main__':
    #qvRealtion(3.65)
    P0 = [1,1,1,1,1]
    r=leastsq(residuals,P0,args=(chargeVoltage,chargeSOC))
    print r[0]
    plotfun(r[0])
    #result:[ 3.346366    0.59163954 -0.00542907 -0.0092671  -0.06431112]







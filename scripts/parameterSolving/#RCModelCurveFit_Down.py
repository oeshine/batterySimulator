import numpy as np
import matplotlib.pylab as plt
from scipy.optimize import leastsq

#P0 =[3.7638,-0.00013,0.3650,0.2201,-0.0272]
#real parameter[ 3.346366,0.59163954,0.00542907,-0.0092671,-0.06431112]
#R1,C1=[  1.71636726e-02   3.40742156e+02]
data=np.loadtxt('batteryModel2.txt',dtype=np.float)
timeZero = 1009
timeEnd = 1742
i=2.652
R0=0.02564
time=data[timeZero:timeEnd,0].astype(np.integer) -timeZero
current=data[timeZero:timeEnd,1]
ternimalVOltage=data[timeZero:timeEnd,2]
dischargeSOC=data[timeZero:timeEnd,3]
def getDischargeSOC(t):
    return dischargeSOC[t]
def dischargeCurrent(t):
    return dischargeCurrent[t]
def RCVoltage(t,P):
    R1,C1=P
    RCVoltage=(-i*R1)*np.exp(-t.astype(np.float)/(R1*C1))+i*R1
    return RCVoltage  
def OCVVoltage(t):
    Zk = dischargeSOC[t]
    K0,K1,K2,K3,K4=[ 3.34636559,0.59164014,0.00542908,-0.00926729,-0.06431107]
    return K0+K1*Zk-K2/Zk+K3*np.log(Zk)+K4*np.log(1-Zk)
    
def dischargeTerminalVoltage(t,P):
    dischargeTerminalVoltage=OCVVoltage(t)-R0*i-RCVoltage(t,P)
    return dischargeTerminalVoltage
    
# def residuals(P,Yk,Zk):
    # err = Yk-fun(Zk,P)
    # return err
    
def residuals(P,Ut,t):
    err = Ut - dischargeTerminalVoltage(t,P)
    return err
def plotTerminalVoltage(P,P0=None):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('Time(S)')
    ax.set_ylabel('Voltage(V)')
    plt.plot(time,dischargeTerminalVoltage(time,P) , label=u"estimated")
    plt.plot(time,ternimalVOltage , label=u"real")
    #ax.xaxis.set_ticks([0,100,200,300,400,500,600,700,800,900])
    ax.grid(True)
    if not P0 is None:
        plt.plot(time,dischargeTerminalVoltage(time,P0) , label=u"initial estimate")
    plt.legend()
    plt.show()  
def plotInitialState(P):

    fig = plt.figure()
    ax = fig.add_subplot(3, 1, 1)
    ax.set_xlabel('Time(S)')
    ax.set_ylabel('Current(A)')
    ax.set_ylim(-0.1,3)
    ax.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
    ax.grid(True)
    ax.plot(time,current,'r',label='Current')
    ax.legend(loc="upper right")


    ax2 = fig.add_subplot(3, 1, 2)
    ax2.set_ylim(3.463,3.625)
    ax2.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
    ax2.grid(True)
    ax2.plot(time,ternimalVOltage,'b',label='Voltage')
    ax2.set_ylabel('Voltage(V)')
    ax2.set_xlabel('Time(S)')
    ax2.legend(loc="lower right")

    ax3 = fig.add_subplot(3, 1, 3)
    ax3.set_ylim(0.3393,0.46)
    ax3.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
    ax3.grid(True)
    ax3.plot(time,dischargeSOC,'b',label='SOC')
    ax3.set_ylabel('SOC')
    ax3.set_xlabel('Time(S)')
    ax3.legend(loc="upper right")
    ax.plot()
    plt.show()

P0=[0.0186,69176]   
print RCVoltage(time,P0) 
#plotVoltage(P0)    
r=leastsq(residuals,P0,args=(ternimalVOltage,time))
print r[0]
plotTerminalVoltage(r[0],P0)
  
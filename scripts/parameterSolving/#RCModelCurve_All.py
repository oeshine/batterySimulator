import numpy as np
import matplotlib.pylab as plt
from scipy.optimize import leastsq

#P0 =[3.7638,-0.00013,0.3650,0.2201,-0.0272]
#real parameter[ 3.346366,0.59163954,0.00542907,-0.0092671,-0.06431112]
#R1,C1=[  1.71636726e-02   3.40742156e+02]
data=np.loadtxt('batteryModel2.txt',dtype=np.float)
timeZero = 0
timeEnd = data.shape[0]
i=2.652
R0=0.02564
time=data[timeZero:timeEnd,0].astype(np.integer) -timeZero
current=data[timeZero:timeEnd,1]
ternimalVOltage=data[timeZero:timeEnd,2]
dischargeSOC=data[timeZero:timeEnd,3]

def OCVVoltage(Zk):
    K0,K1,K2,K3,K4=[ 3.34636559,0.59164014,0.00542908,-0.00926729,-0.06431107]
    return K0+K1*Zk+K2/Zk+K3*np.log(Zk)+K4*np.log(1-Zk)
OCV = OCVVoltage(dischargeSOC)    
def plotInitialState(P):

    fig = plt.figure()
    ax = fig.add_subplot(4, 1, 1)
    ax.set_xlabel('Time(S)')
    ax.set_ylabel('Current(A)')
    ax.set_ylim(-0.1,3)
    ax.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
    ax.grid(True)
    ax.plot(time,current,'r',label='Current')
    ax.legend(loc="upper right")


    ax2 = fig.add_subplot(4, 1, 2)
    ax2.set_ylim(3.463,3.625)
    ax2.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
    ax2.grid(True)
    ax2.plot(time,ternimalVOltage,'b',label='Voltage')
    ax2.set_ylabel('Voltage(V)')
    ax2.set_xlabel('Time(S)')
    ax2.legend(loc="lower right")

    ax3 = fig.add_subplot(4, 1, 3)
    ax3.set_ylim(0.3393,0.46)
    ax3.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
    ax3.grid(True)
    ax3.plot(time,dischargeSOC,'b',label='SOC')
    ax3.set_ylabel('SOC')
    ax3.set_xlabel('Time(S)')
    ax3.legend(loc="upper right")
    ax3.plot()
    
    ax4 = fig.add_subplot(4, 1, 4)
    #ax4.set_ylim(0.3393,0.46)
    ax4.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
    ax4.grid(True)
    ax4.plot(time,OCV,'b',label='OCV')
    ax4.set_ylabel('OCV(V)')
    ax4.set_xlabel('Time(S)')
    ax4.legend(loc="upper right")
    ax4.plot()
    
    plt.show()
P0=[0.0176,340] 
plotInitialState(P0)
  
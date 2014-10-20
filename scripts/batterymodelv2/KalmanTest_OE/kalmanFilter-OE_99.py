import  numpy as np
from numpy.linalg import inv
import matplotlib.pylab as plt
import random
from scipy import interpolate
#time step of mobile movement 
dt = 0.1
data=np.loadtxt('MeasuredData.txt',dtype=np.float)
timeArr=data[:,0]
currentArr=data[:,1]
voltageArr=data[:,2]
#print voltageArr[0],voltageArr[1]
data2=np.loadtxt('Realdata.txt',dtype=np.float)#dataList.append((device.time,device.current,device.voltage,device.soc))
realSocTimeArr=data2[:,0]
realSocArr=data2[:,3]
realVoltageArr=data2[:,2]
#print realVoltageArr[0]
#parameter of the battery model
Rp=0.017163
Cp=2000.74
Rint= 0.02564
K0=3.346366
K1=0.591639
K2=0.005429
K3=-0.009267
K4=-0.064311
Qn=5.3*3600 #As
kalmanGain=[]
clombSOC=[]

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
              
def qvRealtion(voltage):
    global chargeVoltage, chargeQuantity
    vPoints=chargeVoltage
    qPoints=chargeQuantity
    #SOCPoints=chargeSOC
    qvCurveTck=interpolate.splrep(vPoints,qPoints,s=0.002)
    batteryQuantity=interpolate.splev(voltage,qvCurveTck,der=0)
    return batteryQuantity
        
def kf_predict(X, P, A, Q, B, U,it):
    #import pdb; pdb.set_trace()
    X = np.dot(A, X) + np.dot(B, U)*0.7
    P = np.dot(A, np.dot(P, A.T)) + Q 
    return(X,P) 
    
def kf_update(X, P, Y, H, R,U,it): 
    #if it>2000:import pdb; pdb.set_trace()
    IM = K0+np.dot(H, X)-Rint*U[0,0]  #SSF see here!!!!!!
    IS = R + np.dot(H, np.dot(P, H.T)) 
    K = np.dot(P, np.dot(H.T, inv(IS)))
    kalmanGain.append(K)
    X = X + np.dot(K, (Y-IM)) 
    #P = P - np.dot(K, np.dot(IS, K.T)) 
    P=P-np.dot(np.dot(K,H),P)
    return (X,P,K,IM,IS)


# Initialization of state matrices
# X: the state 
#X=[[soc],[Vp]] Vp:RC voltage
#Y:terminal voltage Vt
# P state covariance matrix
# A:state obverse matrix
# Q:process noise covariance matrix
# B:Process covariance matrix F=
# U: the measurement

X=np.array([[0.6],[0]])#2592.14096604,3.6472383191 soc :0.4890832011396226
P = np.diag((0.01, 0.01))
A=np.array([[1.0,0.0],[0.0,np.exp(-1.0/(Rp*Cp))]])
Q = np.eye(X.shape[0]) 
B = np.array([[1.0/Qn],[Rp*(1.0-np.exp(-1.0/(Rp*Cp)))]])
U = np.array([[0.0]])
# print 'X',X
# print 'P',P
# print 'A',A
# print 'Q',Q
# print 'B',B
# print 'U',U
# R:measurement covariance
# H:observation matrices

R=np.array([[0.005]])
H=np.array([[K1-K2/X[0,0]**2+K3/X[0,0]-K4/(1-X[0,0]), -1]])
Y=np.array([[3.64]])
 
# Number of iterations in Kalman Filter 
N_iter =7000#len(currentArr)

# Applying the Kalman Filter 
lastT=0
EstimatedSOCList=[]
deltaTList=[]
lastClombSOC=0
for i in np.arange(0, N_iter):
    #predict matrices for Kalman Filter
    U=np.array([[currentArr[i]]])
    #U=np.array([[10]])
    deltaT=timeArr[i]-lastT
    lastT=timeArr[i]
    if deltaT<=0:
        continue
    deltaTList.append(i)
    tmp=np.exp(-deltaT/(Rp*Cp))
    A=np.array([[1.0,0.0],[0.0,tmp]])
    B=np.array([[deltaT/Qn],[Rp*(1.0-tmp)]])

    (X, P) = kf_predict(X, P, A, Q, B, U,i)
    #update
    SOC=X[0,0]
    Up=X[1,0]
    #print SOC
    # real  sensor input
    Y=np.array([[voltageArr[i]]])
    EstimatedSOCList.append((timeArr[i],SOC,Y,Up,U[0,0]))
    H=np.array([[K1-K2/SOC**2.0+K3/SOC-K4/(1.0-SOC),-1.0]])  
    (X, P, K, IM, IS) = kf_update(X, P, Y, H, R ,U, i)
    lastClombSOC=lastClombSOC+(-currentArr[i]+ random.gauss(300,0.25)*deltaT)/Qn
    clombSOC.append(qvRealtion(voltageArr[0])/5300+lastClombSOC) 
    
EstimatedSOCArr = np.array(EstimatedSOCList)
kalmanGainArr=np.array(kalmanGain)
np.savetxt('kalmanGain.txt',kalmanGainArr,delimiter='\t')

fig= plt.figure()
ax = fig.add_subplot(1,1,1)
ax.set_xlabel('Time(s)')
ax.set_ylabel('SOC')
ax.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,1],'b',label='EKF Eestimated SOC')
ax.plot(realSocTimeArr[:N_iter],realSocArr[:N_iter],'r--',label='Real SOC')
ax.plot(EstimatedSOCArr[:,0],clombSOC,'g',label='Coulomb Counting Estimated SOC')
ax.grid(True)
ax.legend(loc = 'upper right')
# ax2 = ax.twinx()
# ax2.set_ylabel('Error')
# ax2.plot(EstimatedSOCArr[:,0],abs(EstimatedSOCArr[100:,1]-realSocArr[100:N_iter]),'y--',label='EKF Error')
# ax2.plot(EstimatedSOCArr[:,0],abs(clombSOC-realSocArr[:N_iter]),'y',label='Coulomb Counting Error')
# ax2.grid(True)
# ax2.legend(loc = 'lower right')
# ax2 = ax.twinx()
# ax2.set_ylabel('Voltage(V)')
# ax2.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,2],'b',label='measured voltage')
# #ax2.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,3],'y',label='RC voltage')
# ax2.legend(loc='lower right')

# ax3=fig.add_subplot(3,1,2)
# ax3.set_xlabel('Time(S)')
# ax3.set_ylabel('Current(A)')
# ax3.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,4],'g',label='measured current')
# ax3.grid(True)
# ax3.legend(loc='upper right')

# ax4=fig.add_subplot(3,1,3)
# ax4.set_xlabel('Time(S)')
# ax4.set_ylabel('Kalman Gain')
# ax4.plot(EstimatedSOCArr[:,0],kalmanGainArr[:,0,0],'r',label='Kalman Gain SOC')
# ax4.plot(EstimatedSOCArr[:,0],kalmanGainArr[:,1,0],'g',label='Kalman Gain VRC')
# ax4.grid(True)
# ax4.legend(loc='upper right')

plt.show()

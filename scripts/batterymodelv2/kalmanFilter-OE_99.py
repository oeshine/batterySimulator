import  numpy as np
from numpy.linalg import inv
import matplotlib.pylab as plt
import random
#time step of mobile movement 
dt = 0.1
data=np.loadtxt('MeasuredData.txt',dtype=np.float)
timeArr=data[:,0]
currentArr=data[:,1]
voltageArr=data[:,2]

data2=np.loadtxt('Realdata.txt',dtype=np.float)#dataList.append((device.time,device.current,device.voltage,device.soc))
realSocTimeArr=data2[:,0]
realSocArr=data2[:,3]
realVoltageArr=data2[:,2]
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

X=np.array([[0.8],[0]])#2592.14096604,3.6472383191 soc :0.4890832011396226
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
    
EstimatedSOCArr = np.array(EstimatedSOCList)
kalmanGainArr=np.array(kalmanGain)
np.savetxt('kalmanGain.txt',kalmanGainArr,delimiter='\t')

fig= plt.figure()
ax = fig.add_subplot(3,1,1)
ax.set_xlabel('Time(s)')
ax.set_ylabel('SOC')
ax.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,1],'r',label='Eestimated SOC')
ax.plot(realSocTimeArr[:N_iter],realSocArr[:N_iter],'b--',label='Real SOC')
ax.grid(True)
ax.legend(loc = 'upper left')

ax2 = ax.twinx()
ax2.set_ylabel('Voltage(V)')
ax2.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,2],'b',label='measured voltage')
#ax2.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,3],'y',label='RC voltage')
ax2.legend(loc='lower left')

ax3=fig.add_subplot(3,1,2)
ax3.set_xlabel('Time(S)')
ax3.set_ylabel('Current(A)')
ax3.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,4],'g',label='measured current')
ax3.grid(True)
ax3.legend(loc='upper right')

ax4=fig.add_subplot(3,1,3)
ax4.set_xlabel('Time(S)')
ax4.set_ylabel('Kalman Gain')
ax4.plot(EstimatedSOCArr[:,0],kalmanGainArr[:,0,0],'r',label='Kalman Gain SOC')
ax4.plot(EstimatedSOCArr[:,0],kalmanGainArr[:,1,0],'g',label='Kalman Gain VRC')
ax4.grid(True)
ax4.legend(loc='upper right')

plt.show()

import  numpy as np
from numpy.linalg import inv
import matplotlib.pylab as plt

#time step of mobile movement 
dt = 0.1
data=np.loadtxt('TerminalData.txt',dtype=np.float)
timeArr=data[:,0]
currentArr=data[:,1]
voltageArr=data[:,2]

data2=np.loadtxt('OCVdata.txt',dtype=np.float)#dataList.append((device.time,device.current,device.voltage,device.soc))
realSocTimeArr=data2[:,0]
realSocArr=data2[:,3]
#parameter of the battery model
Rp=0.017163
Cp=2000.74
Rint= 0.02564
K0=3.346366
K1=0.591639
K2=0.005429
K3=-0.009267
K4=-0.064311

def kf_predict(X, P, A, Q, B, U): 
    X = np.dot(A, X) + np.dot(B, U) 
    P = np.dot(A, np.dot(P, A.T)) + Q 
    return(X,P) 
    
def kf_update(X, P, Y, H, R): 
    #import pdb; pdb.set_trace()
    IM = K0+np.dot(H, X) 
    IS = R + np.dot(H, np.dot(P, H.T)) 
    K = np.dot(P, np.dot(H.T, inv(IS))) 
    X = X + np.dot(K, (Y-IM)) 
    P = P - np.dot(K, np.dot(IS, K.T)) 
    #LH = gauss_pdf(Y, IM, IS) 
    return (X,P,K,IM,IS)

# get Predictive  probability  (likelihood)  of  measurement    
def gauss_pdf(X, M, S): 

    if M.shape[1] == 1: 
        DX = X - np.tile(M, X.shape[1]) 
        E = 0.5 * np.sum(DX * (np.dot(inv(S), DX)), axis=0) 
        E = E + 0.5 * M.shape[0] * np.log(2 * np.pi) + 0.5 * np.log( np.linalg.det(S)) 
        P =  np.exp(-E) 
    elif X.shape[1] == 1: 
        DX = np.tile(X, M.shape[1])- M 
        E = 0.5 * np.sum(DX * (np.dot(inv(S), DX)), axis=0) 
        E = E + 0.5 * M.shape[0] * np.log(2 * np.pi) + 0.5 * np.log( np.linalg.det(S)) 
        P =  np.exp(-E) 
    else: 
        DX = X-M 
        E = 0.5 * np.dot(DX.T, np.dot(inv(S), DX)) 
        E = E + 0.5 * M.shape[0] * np.log(2 * np.pi) + 0.5 * np.log( np.linalg.det(S)) 
        P =  np.exp(-E) 
        
    return (P[0],E[0]) 

# Initialization of state matrices
# X: the state 
#X=[soc
#    Vp] Vp:RC voltage
#Y:terminal voltage Vt
# P state covariance matrix
# A:state obverse matrix
# Q:process noise covariance matrix
# B:Process covariance matrix F=
# U: the measurement

X=np.array([[0.3],[0]])#2592.14096604,3.6472383191 soc :0.4890832011396226
P = np.diag((0.01, 0.01))
A=np.array([[1,0],[0,0.8424]])
Q = np.eye(X.shape[0]) 
B = np.array([[0.1887],[0.0145]])
U = np.zeros((1,1))

# Measurement matrices 
# Y = np.array([[X[0,0] + abs(np.random.randn(1)[0])], [X[1,0] +abs(np.random.randn(1)[0])]]) 
# H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]]) 
# R = np.eye(Y.shape[0])
# R:measurement covariance
# H:observation matrices
# Y: measurement matrices 

R=np.array([[0.005]])
H=np.array([[1.0955, -1]])
Y=np.array([[3.64]])
 
# Number of iterations in Kalman Filter 
N_iter =200#len(currentArr)
#XX = np.zeros((N_iter,2))
#YY = np.zeros((N_iter,2))
#print 'this is XX',XX
#print 'this is YY',YY
# Applying the Kalman Filter 
lastT=0
Vp=0
EstimatedSOCList=[]
for i in np.arange(0, N_iter):
    #predict
    #matrices for Kalman Filter
    U=np.array([[currentArr[i]]])
    deltaT=timeArr[i]-lastT
    lastT=timeArr[i]
    #print 'deltaT',deltaT
    if deltaT<=0:
        continue
    tmp=np.exp(-deltaT/(Rp*Cp))
    A=np.array([[1,0],[0,tmp]])
    B=np.array([[deltaT/5.3],[Rp*(1-tmp)]])
    (X, P) = kf_predict(X, P, A, Q, B, U)
    #print i,X
    #update
    SOC=X[0,0]
    EstimatedSOCList.append((timeArr[i],SOC))
    Y=np.array([[voltageArr[i]]])
    #print Y
    H=np.array([[K1-K2/(SOC**2)+K3/SOC-K4/(1-SOC),-1]])
    # real  sensor input
    #Y=np.dot(H,X)+np.dot(np.array(-Rint),U)
    #print 'time:',timeArr[i],SOC,Y
    print '.',
    (X, P, K, IM, IS) = kf_update(X, P, Y, H, R)
EstimatedSOCArr = np.array(EstimatedSOCList)
plt.plot(EstimatedSOCArr[:,0],EstimatedSOCArr[:,1],'r',label='Eestimated SOC')
plt.plot(realSocTimeArr[:N_iter*2],realSocArr[:N_iter*2],'b--',label='Real SOC')
#plt.plot(timeArr,voltageArr,'g--',label='Terminal Voltage')
plt.legend(loc = 'lower right')
plt.show()
#kf_update(X, P, Y, H, R)

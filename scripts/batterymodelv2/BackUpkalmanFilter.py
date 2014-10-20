import  numpy as np
from numpy.linalg import inv
import matplotlib.pylab as plt

#time step of mobile movement 
dt = 0.1
data=np.loadtxt('TerminalData.txt',dtype=np.float)
timeArr=data[:,0]
currentArr=data[:,1]
voltageArr=data[:,2]
#parameter of the battery model
Rp=0.017163
Cp=2000.74
Rint= 0.02564
K1=0.591639
K2=0.005429
K3=-0.009267
K4=-0.064311

def kf_predict(X, P, A, Q, B, U): 
    X = np.dot(A, X) + np.dot(B, U) 
    P = np.dot(A, np.dot(P, A.T)) + Q 
    return(X,P) 
    
def kf_update(X, P, Y, H, R): 
    IM = np.dot(H, X)
    print 'IM',IM.shape,IM
    #Hnew=H[np.newaxis]
    IS = R + np.dot(H, np.dot(P, H.T))
    print 'H',H.shape,H
    print 'H.T',(H.T).shape,H.T
    print 'IS',IS.shape,IS
    print 'inv(IS)',inv(IS).shape,inv(IS)
    IA=np.dot(H.T, inv(IS))
    K = np.dot(P, IA) 
    print  'IA',IA.shape,IA
    print 'K',K.shape,K
    print 'Y-IM',( Y-IM).shape,Y-IM
    X = X + np.dot(K, Y-IM)
    print 'X' ,X.shape,X
    P = P - np.dot(K, np.dot(IS, K.T)) 
    print 'P',P.shape,P
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

X=np.array([[0.4891],[0]])#2592.14096604,3.6472383191 soc :0.4890832011396226
P = np.diag((0.01, 0.01))
A=np.array([[1,0],[0,0.8424]])
Q = np.eye(X.shape[0]) 
B = np.array([0.1887,0.0145])
U = np.zeros((X.shape[0],1))


# Measurement matrices 
# Y = np.array([[X[0,0] + abs(np.random.randn(1)[0])], [X[1,0] +abs(np.random.randn(1)[0])]]) 
# H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]]) 
# R = np.eye(Y.shape[0])
# R:measurement covariance
# H:observation matrices
# Y: measurement matrices 

R=np.array([[0.005,0],[0,0.0191]])
H=np.array([1.0955, -1])
Y=np.array([[4.2],[1.3]])
 
# Number of iterations in Kalman Filter 
N_iter = 4
#XX = np.zeros((N_iter,2))
#YY = np.zeros((N_iter,2))
#print 'this is XX',XX
#print 'this is YY',YY
# Applying the Kalman Filter 
lastT=0
Vp=0
SOCList=[]
for i in np.arange(0, N_iter):
    #predict
    #matrices for Kalman Filter
    U=currentArr[i]
    #print U
    #deltaT=timeArr[i]-lastT
    #lastT=timeArr[i]
    #print 'deltaT',deltaT
    #if deltaT==0:
        #continue
    deltaT=0.01
    tmp=np.exp(-deltaT/(Rp*Cp))
    
    A=np.array([[1,0],[0,tmp]])
    B=np.array([[deltaT/5.3],[Rp*(1-tmp)]])
    X=np.dot(A,X)+np.dot(B,U)
    (X, P) = kf_predict(X, P, A, Q, B, U)
    #XX[i,0] = i
    #XX[i,1] = X[0]
    #update
    SOC=X[0,0]
    SOCList.append(SOC)
    H=np.array([K1-K2/(SOC**2)+K3/SOC-K4/(1-SOC),-1])
    # real  sensor input
    #Y=np.dot(H,X)+np.dot(np.array(-Rint),U)
    Y=voltageArr[i]
    #print Y
    #YY[i,0] = i
    #YY[i,1] = Y
    (X, P, K, IM, IS) = kf_update(X, P, Y, H, R)
#print SOCList
#plt.plot(XX[:,0],XX[:,1],'r',label='index')
#plt.plot(YY[:,0],YY[:,1],'g--',label='voltage')
#plt.plot(timeArr,voltageArr,'b',label='ternimal voltage')
#plt.plot(timeArr,SOCList,'r',label='SOC')
#plt.plot(timeArr,currentArr,'y',label='current')
#plt.legend()
#plt.show()
#kf_update(X, P, Y, H, R)

import  numpy as np
from numpy.linalg import inv
import matplotlib.pylab as plt

#time step of mobile movement 
dt = 0.1 
def kf_predict(X, P, A, Q, B, U): 
    X = np.dot(A, X) + np.dot(B, U) 
    P = np.dot(A, np.dot(P, A.T)) + Q 
    return(X,P) 
    
def kf_update(X, P, Y, H, R): 
    IM = np.dot(H, X) 
    IS = R + np.dot(H, np.dot(P, H.T)) 
    K = np.dot(P, np.dot(H.T, inv(IS))) 
    X = X + np.dot(K, (Y-IM)) 
    P = P - np.dot(K, np.dot(IS, K.T)) 
    LH = gauss_pdf(Y, IM, IS) 
    return (X,P,K,IM,IS,LH)

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
"""
X: the state 
P state covariance matrix
A:state obverse matrix
Q:process noise covariance matrix
B:Process covariance matrix
U: the measurement
""" 
X = np.array([[0.0], [0.0], [0.1], [0.1]])
P = np.diag((0.01, 0.01, 0.01, 0.01)) 
A = np.array([[1, 0, dt , 0], [0, 1, 0, dt], [0, 0, 1,0], [0, 0, 0,1]]) 
Q = np.eye(X.shape[0]) 
B = np.eye(X.shape[0]) 
U = np.zeros((X.shape[0],1)) 
print X
# Measurement matrices 
Y = np.array([[X[0,0] + abs(np.random.randn(1)[0])], [X[1,0] +abs(np.random.randn(1)[0])]]) 
H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]]) 
R = np.eye(Y.shape[0]) 
# Number of iterations in Kalman Filter 
N_iter = 50

XX = np.zeros((N_iter,2))
YY = np.zeros((N_iter,2))
# Applying the Kalman Filter 
for i in np.arange(0, N_iter): 
    #predict
    (X, P) = kf_predict(X, P, A, Q, B, U)
    XX[i,0] = i
    XX[i,1] = X[0]
    YY[i,0] = i
    YY[i,1] = Y[0]
    #update
    (X, P, K, IM, IS, LH) = kf_update(X, P, Y, H, R)
    # create a random sensor input
    Y = np.array([[X[0,0] + abs(0.1 * np.random.randn(1)[0])],[X[1,0] +abs(0.1 * np.random.randn(1)[0])]])
plt.plot(XX[:,0],XX[:,1],'r')
plt.plot(YY[:,0],YY[:,1],'g--')
plt.show()

import numpy as np
import matplotlib.pylab as plt
from scipy import interpolate

fig= plt.figure()
fig.suptitle('Estimated SOC and Real SOC Comparation',fontsize=14,fontweight='bold')
ax = fig.add_subplot(1,1,1)
ax.set_xlabel('Time(s)')
ax.set_ylabel('SOC')
calSOC=[]
dischargeSOC=[]
x=[]
y=[]
x1=[]
y1=[]
error=[]
dischargeSOCValue=[]
calSOC=np.loadtxt('calSOC.txt',dtype=np.float)
dischargeSOC=np.loadtxt('dischargeData.txt',dtype=np.float)
x=calSOC[:,0]
y=calSOC[:,1]
x1=dischargeSOC[:,0]
y1=dischargeSOC[:,1]
# for index in range(len(y)):
    # error.append(y1[index]-y[index])
# print error
dischargeSOCdict={}
for index in range(len(y1)):
    dischargeSOCdict[x1[index]] = y1[index]
for element in x:
    dischargeSOCValue.append(dischargeSOCdict[element])
print dischargeSOCValue

for index in range(len(y)):
    error.append(y[index] - dischargeSOCValue[index])
    
ax.plot(x,y,'g',label='Estimated SOC')
ax.plot(x1,y1,'b',label='Real SOC')
ax.plot(x,error,'r--',label='Error')
ax.legend()
plt.show()
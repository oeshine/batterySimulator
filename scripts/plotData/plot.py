import matplotlib.pylab as plt
import numpy as np

data=np.loadtxt('PID.txt',dtype=np.float)
print('shape of data:' + str(data.shape))

# plot the data
fig = plt.figure()
fig.suptitle('Cell Balance Plot',fontsize=14,fontweight='bold')
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('Time(S)')
ax.set_ylabel('Voltage(V)')

for index in range(0,data.shape[1],8):
    ax.plot(data[:,index], data[:,index+1], 'r')
    ax.plot(data[:,index+2], data[:,index+3], 'g')
    ax.plot(data[:,index+4], data[:,index+5], 'b')
    ax.plot(data[:,index+6], data[:,index+7], 'y')
plt.show()
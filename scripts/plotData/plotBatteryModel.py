from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import numpy as np

data=np.loadtxt('batteryModel2.txt',dtype=np.float)
#print type(data)
# plot the data
fig = plt.figure()
fig.suptitle('Battery Ternimal Voltage Response',fontsize=14)
ax = fig.add_subplot(2, 1, 1)
ax.set_xlabel('Time(S)')
ax.set_ylabel('Current(A)')
ax.set_ylim(-0.1,3)
ax.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
ax.grid(True)
ax.plot(data[600:2500,0],data[600:2500,1],'r',label='Current')
#ax.plot(data[112,0],data[112,1],'rs',label='Imax,i')
#ax.plot(data[111,0],data[111,1],'bo',label='Imin,i')
ax.legend(loc="upper right")


ax2 = fig.add_subplot(2, 1, 2)
ax2.set_ylim(3.46,3.65)
ax2.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
ax2.grid(True)
ax2.plot(data[600:2500,0],data[600:2500,2],'b',label='Voltage')
#ax2.plot(data[111,0],data[111,2],'rs',label='Vmax,i')
#ax2.plot(data[112,0],data[112,2],'bo',label='Vmin,i')
ax2.set_ylabel('Voltage(V)')
ax2.set_xlabel('Time(S)')
ax2.legend(loc="upper right")

# ax3 = fig.add_subplot(3, 1, 3)
# ax3.set_ylim(0.45110,0.45127)
# ax3.xaxis.set_ticks([200,400,600,800,1000,1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400])
# ax3.grid(True)
# ax3.plot(data[:,0],data[:,3],'b',label='SOC')
# ax3.set_ylabel('SOC')
# ax3.set_xlabel('Time(S)')
# ax3.legend(loc="upper right")
ax.plot()
plt.show()

from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import numpy as np
NumberOfCells= 12
NumberOfStacks= 2

y_pos=[4.023, 4.026, 4.033, 4.021, 4.025, 4.027, 4.029, 4.035, 4.025,4.034, 4.021, 4.016, 4.026, 4.026, 4.024, 4.026, 4.033, 4.023, 4.028, 4.016, 4.019, 4.021, 4.023, 4.024]
x_pos=range(24)
print x_pos
x = np.arange(24)

fig, ax = plt.subplots()
ax.set_ylim(4,4.04)
plt.bar(x_pos, y_pos)
plt.xticks( x + 0.5,  x_pos )
plt.xlabel('Cell Name')
plt.ylabel('Cell Voltage(V)')
plt.title('Initial Battery Voltage')
plt.show()


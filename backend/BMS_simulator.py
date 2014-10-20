import os
import argparse
from serial_manager import SerialManager
import numpy as np
import time
import timeit
import PID
import pickle
from scipy import interpolate
import matplotlib.pylab as plt
import random
from scipy.optimize import leastsq

SERIAL_PORT = 'COM4'
BITSPERSECOND = 9600
numberOfCells = 12
numberOfStacks = 2
BATTERYCAPACITY = 5300
strV = []
strB = []
voltage =[0] * numberOfCells * numberOfStacks
pwmout = [0] * numberOfCells * numberOfStacks
outv = [0] * numberOfCells * numberOfStacks
batteryTime = 0
relayStatus = 0
totalVoltage = 0.0
totalCurrent = 0.0
quitFlag = 0

chargeQuantity = [10.0,74.2,159,243.8,328.6,413.4,498.2,583,662.5,747.3,832.1\
               ,916.9,1001.7,1086.5,1171.3,1256.1,1340.9,1425.7,1505.2\
               ,1590,1674.8,1759.6,1844.4,1929.2,2014,2098.8,2183.6,2268.4\
               ,2347.9,2432.7,2517.5,2602.3,2687.1,2771.9,2856.7,2941.5\
               ,3026.3,3111.1,3190.6,3275.4,3360.2,3445,3529.8,3614.6\
               ,3699.4,3784.2,3869,3953.8,4033.3,4118.1,4202.9,4287.7\
               ,4372.5,4457.3,4542.1,4626.9,4711.7,4796.5,4876,4960.8\
               ,5045.6,5130.4,5215.2,5300]
               
chargeVoltage = np.array([2.80,3.023,3.159,3.25,3.318,3.362,3.383,3.398,3.412,3.429,3.446\
              ,3.462,3.477,3.49,3.503,3.513,3.524,3.535,3.545,3.557,3.569\
              ,3.584,3.594,3.601,3.607,3.612,3.618,3.624,3.629,3.635,3.642\
              ,3.648,3.656,3.664,3.672,3.682,3.693,3.706,3.721,3.74,3.761\
              ,3.78,3.797,3.813,3.829,3.846,3.861,3.877,3.893,3.909,3.926\
              ,3.943,3.96,3.978,3.997,4.017,4.037,4.057,4.077,4.096,4.115\
              ,4.135,4.158,4.184])
              
chargeSOC = np.array([0.009,0.014,0.03,0.046,0.062,0.078,0.094,0.11\
				,0.125,0.141,0.157,0.173,0.189,0.205,0.221,0.237\
				,0.253,0.269,0.284,0.3,0.316,0.332,0.348,0.364\
				,0.38,0.396,0.412,0.428,0.443,0.459,0.475,0.491\
				,0.507,0.523,0.539,0.555,0.571,0.587,0.602,0.618\
				,0.634,0.65,0.666,0.682,0.698,0.714,0.73,0.746,0.761\
				,0.777,0.793,0.809,0.825,0.841,0.857,0.873,0.889\
				,0.905,0.92,0.936,0.952,0.968,0.984,0.99])
                
# Setup Argument Parser
argparser = argparse.ArgumentParser(description = 'Run TS_BatterySimulator.', prog = 'TS_BatterySimulator')
argparser.add_argument('port', metavar = 'serial_port', nargs = '?', default = False,help = 'serial port to the Simulator')
args = argparser.parse_args()

if not SERIAL_PORT:

    if args.port:
        # (1) get the serial device from the argument list
        SERIAL_PORT = args.port
        print "Using serial device '" + SERIAL_PORT + "' from command line."
    else:
        print 'Please select a serialport via args'
		
if os.name == 'nt': 
    GUESS_PREFIX = "Arduino"   
elif os.name == 'posix':
    if sys.platform == "linux" or sys.platform == "linux2":
		# match by arduino VID
        GUESS_PREFIX = "2341"  
    else:
        GUESS_PREFIX = "tty.usbmodem"    
else:
    GUESS_PREFIX = "no prefix"  
    
	
def qvRealtion(voltage):

    global chargeVoltage, chargeQuantity
	
    vPoints = chargeVoltage
    qPoints = chargeQuantity
    SOCPoints = chargeSOC
	
    qvCurveTck = interpolate.splrep(vPoints, qPoints, s = 0.002)
    batteryQuantity = interpolate.splev(voltage, qvCurveTck, der = 0)
    SOCVCurveTck = interpolate.splrep(SOCPoints, vPoints,s = 0.002)
    batterySOC = interpolate.splev(voltage, SOCVCurveTck, der = 0)
	
    newX = np.arange(vPoints[0], vPoints[-1], 0.1)
    newY = interpolate.splev(newX, qvCurveTck, der = 0)
	
    plt.plot(vPoints, qPoints, 'o', newX, newY, '-')
    plt.title("V-Q curve")
	
    newSOC = np.arange(SOCPoints[0], SOCPoints[-1], 0.01)
    newVoltage = interpolate.splev(newSOC, SOCVCurveTck, der = 0)
	
    plt.plot(SOCPoints, vPoints, 'o', newSOC, newVoltage, '-')
    plt.title("V-SOC curve")
    plt.show()
	
    return batteryQuantity
	
	
def vqRealtion(batteryQuantity):
	
	global chargeVoltage, chargeQuantity

	vPoints = chargeVoltage
	qPoints = chargeQuantity
	SOCPoints = chargeSOC
	
	vqCurveTck = interpolate.splrep(qPoints, vPoints, s = 0.002)
	batteryVoltage = interpolate.splev(batteryQuantity, vqCurveTck, der = 0)
	
	newX = np.arange(qPoints[0], qPoints[-1], 0.1)
	newY = interpolate.splev(newX, vqCurveTck, der = 0)
	fig = plt.figure()
	fig.suptitle('Q-V curve')
	ax = fig.add_subplot(1, 1, 1)
	ax.set_ylim(2.75,4.2)
	ax.yaxis.set_ticks(np.arange(2.75,4.2,0.05))
	ax.set_xlim(0,5500)
	ax.xaxis.set_ticks(np.arange(0,5500,50))
	ax.grid(True)
	ax.set_xlabel('Battery Quantity(mAh)')
	ax.set_ylabel('Voltage(V)')
	ax.plot(qPoints, vPoints, 'o', newX, newY, '-')
	
	plt.show()
	
	return batteryVoltage
 
 
def commandGenerator():

	global strV
	
	for stackNumber in range(numberOfStacks):
		for cellNumber in range(numberOfStacks):
			strV.append('pvol' + ',' + str(stackNumber) + ',' + str(cellNumber) + ';')
	print strV

			
def sendCommand(command):
	
	#clear rx_buffer
    SerialManager.read_existing() 
	
    if SerialManager.write(command + '\r'):
        return SerialManager.read_to('\r')
    else:
        return 'error'
  
  
def readStatus():

    global totalCurrent, totalVoltage
	
    readVoltage()
	
    totalVoltage=float(sendCommand('rtv;'))
    print 'total voltage is:', totalVoltage
	
    totalCurrent=float(sendCommand('rtc;')) * 1000
    print 'total current is:', totalCurrent

	
def setpwm():

    global batteryTime, pwmout, outv
	
    from batterySimulator import TimeMachine
	
    tm = TimeMachine()
    outvMax = round(max(outv), 4);
    print 'Max output of PID is:',outvMax
	
    for number in range(numberOfCells*numberOfStacks):
        if outvMax != 0:
            pwmout[number] = int(outv[number] * 100 / outvMax)
            sendCommand(strB[number] + str(pwmout[number]))
        else:
			#command for kill the simulation
            sendCommand('K000')  
            quitFlag = 1
			
	#sync the clock by reading clock in the battery simulator
    batteryTime = int(sendCommand('J000')) 
    print 'the current time is:' ,batteryTime

	
def readVoltage():

    global voltage
	
    for index in range(len(strV)):
         voltage[index] = float(sendCommand(strV[index]))
    print'the voltages are:', voltage

    
def pidController(Kp = 1, Ki = 0, Kd = 0):

    #readVoltage() 
    global outv    
	
    ministVoltage = min(voltage)
    if  (2.75 < ministVoltage< 4.20):
        sp = ministVoltage
    else:
        print ' minist voltage Error'
     
    fb = [0] * numberOfCells * numberOfStacks
    err = [0] * numberOfCells * numberOfStacks
    pid = PID.PID()
    pid.SetKp(Kp)
    pid.SetKi(Ki)
    pid.SetKd(Kd)

    for number in range(numberOfCells * numberOfStacks):
        #read the feedback
        fb[number] = voltage[number]
        # calculate the error
        err[number] = fb[number] - sp          
        # PID block
        outv[number] = pid.GenOut(err[number])

        time.sleep(.05)
		
    setpwm()


	
def calSOC():

    f = open('calSOC.txt','a')
    initQuantity = [0] * numberOfCells * numberOfStacks
    initSOC = [0] * numberOfCells * numberOfStacks
    dischargeQuantity = [0] * numberOfCells * numberOfStacks
    SOC = [0] * numberOfCells * numberOfStacks
	
	#sync the clock by reading clock in the battery simulator
    batteryTime = int(sendCommand('J000')) 
    f.write(str(batteryTime) + '\t')
	
    if batteryTime == 0:
        for index in range(len(voltage)):
            initQuantity[index] = qvRealtion(voltage[index])
            initSOC[index] = initQuantity[index] / BATTERYCAPACITY
        totalQuantity = sum(initQuantity)
        totalSOC = totalQuantity / (BATTERYCAPACITY * numberOfCells * numberOfStacks)
        f.write(str(totalSOC)+'\t')
        f.write('\n')
        f.close()
        pickle.dump(initQuantity,open('data.pickle','w'))      
		
    else:
        initialQuantity = pickle.load(open('data.pickle','r'))
        for index in range(len(initialQuantity)):
            dischargeQuantity[index] = initialQuantity[index]- totalCurrent * batteryTime / 3600
            SOC[index] = dischargeQuantity[index] / BATTERYCAPACITY
        totalQuantity = sum(dischargeQuantity)
        totalSOC = totalQuantity / (BATTERYCAPACITY * numberOfCells * numberOfStacks)
        f.write(str(totalSOC) + '\t')
        f.write('\n')
        f.close()
 
 
def infoUpdata():

    f = open('PID.txt','a')
    for number in range(numberOfCells * numberOfStacks):
        f.write(str(batteryTime) + '\t')
        f.write(str(voltage[number]) + '\t')
    f.write('\n')
    f.close()

	
if __name__ == '__main__':

	if not SERIAL_PORT:
		SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)
	SerialManager.connect(SERIAL_PORT, BITSPERSECOND)

	commandGenerator()
	 






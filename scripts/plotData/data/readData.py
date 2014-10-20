import os
import argparse
from serial_manager import SerialManager
SERIAL_PORT = 'COM11'
BITSPERSECOND = 9600

strV=[]
strT=[]
strF=[]

### Setup Argument Parser
argparser = argparse.ArgumentParser(description='Run TS_BatterySimulator.', prog='TS_BatterySimulator')
argparser.add_argument('port', metavar='serial_port', nargs='?', default=False,
                    help='serial port to the Simulator')
args = argparser.parse_args()
if not SERIAL_PORT:
    if args.port:
        # (1) get the serial device from the argument list
        SERIAL_PORT = args.port
        print "Using serial device '"+ SERIAL_PORT +"' from command line."
    else:
        print 'Please select a serialport via args'
if os.name == 'nt': #sys.platform == 'win32': 
    GUESS_PREFIX = "Arduino"   
elif os.name == 'posix':
    if sys.platform == "linux" or sys.platform == "linux2":
        GUESS_PREFIX = "2341"  # match by arduino VID
    else:
        GUESS_PREFIX = "tty.usbmodem"    
else:
    GUESS_PREFIX = "no prefix"   
 
def commandGenerator():

    for stackNumber in range(8):
        for cellNumber in range(12):
            if(cellNumber<10):
                strV.append('V'+str(stackNumber)+'0'+str(cellNumber))
            else:
                strV.append('V'+str(stackNumber)+str(cellNumber))
    #print strV
    
    for stackNumber in range(8):
        for cellNumber in range(2):
             strT.append('T'+str(stackNumber)+'0'+str(cellNumber))
    #print strT
    
    for stackNumber in range(8):
        for cellNumber in range(3):
            strF.append('F'+str(stackNumber)+'0'+str(cellNumber))
    #print strF
 
def checkErr(* flag):
    for index in range(len(flag)):
        if flag[index] != 0:
            SerialManager.read_existing() #clear rx_buffer
            if SerialManager.write('O000'+'\r'):
                relayStatus=SerialManager.read_to('\r')
                print 'relay status is:',relayStatus
                
def checkWarning(*voltage):
    for index in range(len(voltage)):
        if voltage[index] >= 4.05:
            print 'high voltage warning'
        elif voltage[index] <= 2.85:
            print 'low voltage warning'
            
def balancing(stackNum,cellNum):
    balanceCommand='B'+str(stackNum)+str(cellNum)
    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write( balanceCommand +'\r'):
        balanceStartTime=SerialManager.read_to('\r')
        print 'balance start time is:',balanceStartTime 
        
def stopBalancing(stackNum,cellNum):
    balanceCommand='S'+str(stackNum)+str(cellNum)
    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write( balanceCommand +'\r'):
        balanceStopTime=SerialManager.read_to('\r')
        print 'balance stop time is:',balanceStopTime
        
if __name__ == '__main__':
    #if not SERIAL_PORT:
    #    SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)
    commandGenerator();
    flag=[]
    voltage=[]
    temperature=[]
    relayStatus=0
    SerialManager.connect(SERIAL_PORT, BITSPERSECOND)
    #while SerialManager.is_connected():

    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write('C000'+'\r'):
        relayStatus=SerialManager.read_to('\r')
        print 'relay status is:',relayStatus

    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write('R000'+'\r'):
        totalVoltage=SerialManager.read_to('\r')
        print 'total voltage is:',totalVoltage
    
    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write('I000'+'\r'):
        totalCurrent=SerialManager.read_to('\r')
        print 'total current is:', totalCurrent 

    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write('F800'+'\r'):
        readCellFlagStatus=SerialManager.read_to('\r')
        print'read cell flags status is:', readCellFlagStatus
    
    print 'the flags are: '
    for index in range(len(strF)):
        SerialManager.read_existing() #clear rx_buffer
        if SerialManager.write(strF[index]+'\r'):
            flag.append(SerialManager.read_to('\r'))
            #flag[index]=int(flag[index])
            print flag[index]
    checkErr(flag)
            
        
    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write('V800'+'\r'):
        readCellVoltageStatus=SerialManager.read_to('\r')
        print'read cell voltage status is:', readCellVoltageStatus 
    
    print 'the voltages are: '
    for index in range(len(strV)):
        SerialManager.read_existing() #clear rx_buffer
        if SerialManager.write( strV[index]+'\r'):
            voltage.append(SerialManager.read_to('\r'))
            #voltage[index]=float(voltage[index])
            print voltage[index]
    checkWarning(voltage)
    
    maxVoltage=[]
    maxVoltageIndex=[]
    for i in range(8):
        maxVoltage.append(max(voltage[0+i*12 : 11+i*12]))
        maxVoltageIndex.append(voltage.index(max(voltage[0+i*12:11+i*12])))
    print maxVoltage
    print maxVoltageIndex
    
    SerialManager.read_existing() #clear rx_buffer
    if SerialManager.write('T800'+'\r'):
        readCellTemperatureStatus=SerialManager.read_to('\r')
        print'read cell temperature status is:', readCellTemperatureStatus 
    
    print 'the temperatures are: '
    for index in range(len(strT)):
        SerialManager.read_existing() #clear rx_buffer
        if SerialManager.write( strT[index]+'\r'):
            temperature.append(SerialManager.read_to('\r'))
            #temperature[index] =float(temperature[index])
            print temperature[index]
            
    print("Port closed!")







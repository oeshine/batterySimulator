from RealBatteryModelDevices import *
import numpy as np
import eispice
import pickle

realDataList=[]
measureDataList=[]
lastTime=0
lastT=0
def OCVInfoRecorder(device):
    global lastT
    '''
    A callback function to print the runtime status of the OCV device during simulation
    '''
    if device.time > lastT:
        realDataList.append((device.time,device.current,device.voltage,device.soc))
        lastT=device.time
    
    #debugString = "t:{time},v:{voltage},soc:{soc},i:{current}".format(**device.__dict__)
    #print debugString  #print operation will slow down the simulation process! so, here we comment it 
    
def constantCurrentLoad(load):
    global lastTime
    if (load.time) is not None and  (load.current) is not None and  (load.vp-load.vn) is not None:
        if load.time > lastTime:
            measureDataList.append((load.time,load.current,load.vp-load.vn))
            lastTime=load.time
    else:
        print 'none value'
   
    if load.vp>load.vn:
   
        if 100<load.time<1100:
            return 2.652   #discharge
        elif 1100<=load.time<1600:
            return -2.65
        elif 1600<=load.time<2600:
            return 2.652
        elif 2600<=load.time<3100:
            return -2.652   #discharge
        elif 3100<=load.time<4100:
            return 2.652   #discharge
        elif 4100<=load.time<4600:
            return -2.652   #discharge
        elif 4600<=load.time<5600:
            return 2.652   #discharge
        elif 5600<=load.time<6100:
            return -2.652   #discharge  
        else:
            return 0.001
    else:
        return 0.001
            
if __name__ == '__main__':
    
    #define a descriptor list for the battery group
    descriptorLst = []
    for i in range(1):
        des = BatteryDescriptor() 
        des.Name = 'cell' + str(i) # define a name
        des.OCVCallback = OCVInfoRecorder
        # add more customize parameters here
        #...
        descriptorLst.append(des)   
    cct = eispice.Circuit("Battery Group Test")
    #define a battery group with the descriptor list
    cct.bg = RealBatteryGroup(1,eispice.GND,descriptorLst) #print the runtime message
    #add a constant current load (1.0A)
    cct.load = customizedCurrentSource(1,eispice.GND,constantCurrentLoad) 
    print cct.devices() #print the network of the circuit
    cct.tran('1', '7000') #timestep=1 last 25000 seconds
    #here do something after simulation, for example save realDataList
    realDataArr=np.array(realDataList)
    np.savetxt('Realdata.txt',realDataArr,delimiter='\t')
    #print measureDataList
    measureDataArr=np.array(measureDataList)
    np.savetxt('MeasuredData.txt',measureDataArr,delimiter='\t')
    eispice.plot(cct)
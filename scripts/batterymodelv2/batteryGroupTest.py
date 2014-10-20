from RealBatteryModelDevices import *

if __name__ == '__main__':
    
    #define a descriptor list for the battery group
    descriptorLst = []
    for i in range(72):
        des = BatteryDescriptor() 
        des.Name = 'cell' + str(i) # define a name
        des.OCVCallback = printOCVInfo
        # add more customize parameters here
        #...
        
        descriptorLst.append(des)
        
    cct = eispice.Circuit("Battery Group Test")
    #define a battery group with the descriptor list
    cct.bg = RealBatteryGroup(1,eispice.GND,descriptorLst) #print the runtime message
    #add a constant current load (1.0A)
    cct.load = customizedCurrentSource(1,eispice.GND,lambda device:10.0) 
    print cct.devices() #print the network of the circuit
    cct.tran('1', '3200') #timestep=1 last 25000 seconds
    eispice.plot(cct)
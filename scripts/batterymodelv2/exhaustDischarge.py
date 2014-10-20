from RealBatteryModelDevices import *
if __name__ == '__main__':
    defaultDescriptor.InitialSOC = 0.99
    defaultDescriptor.OCVCallback = printOCVInfo
    cct = eispice.Circuit("Exhausted Discharge")
    #define a battery with default battery parameter
    cct.rb = RealBattery(1,eispice.GND,defaultDescriptor) #print the runtime message
    #add a constant current load (10.0A)
    cct.load = customizedCurrentSource(1,eispice.GND,lambda device:10.0 if device.vp>device.vn else 0.001) 
    cct.tran('1', '2200') #timestep=1 last 25000 seconds
    eispice.plot(cct)
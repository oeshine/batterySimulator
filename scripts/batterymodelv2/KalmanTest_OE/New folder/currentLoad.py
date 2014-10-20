from RealBatteryModelDevices import *
import numpy as np
import eispice

realDataListDict={}
realDataList=[]
measureDataList=[]
lastTime=0
NumberOfCells= 12
NumberOfStacks= 2

internalResistance=[ 0.0255,0.0254,0.0253,0.0256,0.0258,0.0160,0.0251,0.0250,0.0252,0.0255,0.0259,0.0252\
                    ,0.0250,0.0258,0.0254,0.0255,0.0252,0.0254,0.0259,0.0250,0.0257,0.0251,0.0250,0.0161\
                    ,0.0253,0.0257,0.0254,0.0250,0.0149,0.0253,0.0255,0.0258,0.0252,0.0257,0.0255,0.0255\
                    ,0.0254,0.0252,0.0250,0.0148,0.0250,0.0251,0.0255,0.0257,0.0252,0.0259,0.0161,0.0257\
                    ,0.0252,0.0255,0.0255,0.0255,0.0258,0.0259,0.0252,0.0254,0.0256,0.0259,0.0251,0.0253\
                    ,0.0259,0.0253,0.0256,0.0251,0.0254,0.0253,0.0257,0.0258,0.0250,0.0255,0.0255,0.0253\
                    ,0.0255,0.0253,0.0258,0.0252,0.0160,0.0250,0.0254,0.0258,0.0258,0.0253,0.0252,0.0259\
                    ,0.0255,0.0254,0.0258,0.0259,0.0258,0.0253,0.0255,0.0255,0.0255,0.0255,0.0252,0.0255]

                    
initialQuantity=[4640,4650,4680,4630,4648,4655,4666,4690,4646,4687,4632,4611\
                ,4650,4654,4644,4651,4680,4639,4659,4611,4620,4629,4639,4642\
                ,4643,4646,4650,4660,4670,4630,4660,4670,4650,4640,4630,4668\
                ,4645,4659,4644,4649,4641,4655,4653,4621,4633,4659,4652,4638\
                ,4677,4652,4657,4663,4666,4629,4649,4633,4644,4655,4666,4634\
                ,4628,4624,4632,4670,4656,4635,4639,4659,4639,4670,4680,4650\
                ,4637,4650,4660,4630,4680,4620,4670,4640,4667,4655,4636,4651\
                ,4637,4682,4684,4633,4644,4622,4629,4627,4639,4649,4636,4621]
                
                
def OCVInfoRecorder(device):
    '''
    A callback function to print the runtime status of the OCV device during simulation
    '''
    if device.name in realDataListDict:
        if device.time > realDataListDict[device.name][-1][0]:
            #import pdb; pdb.set_trace()
            realDataListDict[device.name].append((device.time,device.current,device.voltage,device.soc))#append a dictionary with key of the name here
    else:
        realDataListDict[device.name] = [(device.time,device.current,device.voltage,device.soc)]
        

    
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
        if 1500<load.time<2500:
            return 2.652   #discharge
        elif 2500<=load.time<3500:
            return 0.001
        elif 3500<=load.time<4500:
            return -2.652
        elif 4500<=load.time<5500:
            return 2.652   #discharge
        else:
            return 0.001
    else:
        return 0.001
            
if __name__ == '__main__':
    
    #define a descriptor list for the battery group
    descriptorLst = []
    for i in range(NumberOfStacks*NumberOfCells):
        des = BatteryDescriptor() 
        des.Name = 'cell' + str(i) # define a name
        des.InnerR=float(internalResistance[i])
        des.InitialSOC=float(initialQuantity[i])/5300
        des.OCVCallback = OCVInfoRecorder
        # add more customize parameters here
        #...
        descriptorLst.append(des)   
    cct = eispice.Circuit("Battery Group Test")
    #define a battery group with the descriptor list
    cct.bg = RealBatteryGroup(1,eispice.GND,descriptorLst) #print the runtime message
    #add a constant current load (1.0A)
    cct.load = customizedCurrentSource(1,eispice.GND,constantCurrentLoad) 
    #print cct.devices() #print the network of the circuit
    cct.tran('1', '7000') #timestep=1 last 25000 seconds
    #here do something after simulation, for example save realDataList
    for i in realDataListDict.keys():
        realDataArr=np.array(realDataListDict[i])
        np.savetxt(i+'_Realdata.txt',realDataArr,delimiter='\t')
    #print measureDataList
    measureDataArr=np.array(measureDataList)
    np.savetxt('MeasuredData.txt',measureDataArr,delimiter='\t')
    eispice.plot(cct)
import eispice
import numpy as np
import time
import subckt

class BatteryDescriptor():
    '''
    Parameters to construct a battery model
    '''
    OCV_SOC_Parameters =(3.346366,0.591639,0.005429,-0.009267,-0.064311)
    def __init__(self):
        self.Name = 'cell'
        self.OCVParameter = self.OCV_SOC_Parameters
        self.InnerR =  0.02564
        self.R1 = 0.017163
        self.C1 = 2000.74
        self.R2 = None
        self.C2 = None
        self.InitialSOC = 0.451251623
        self.Capacity = 5300
        self.OCVCallback = None 
        self.BalanceResCallBack = None #None means no balance resistance needed

defaultDescriptor = BatteryDescriptor()

class OCV(eispice.PyB):
  '''
  Open circuit Voltage device model
  calculate with the following equation:
   K0+K1*soc-K2/soc+K3*np.log(soc)+K4*np.log(1-soc)
  '''
  def __init__(self, pNode,nNode,p,initialSOC,capacity,name,runTimeCallback=None):
    '''
    initialSOC: ?%
    capacity: mAh
    name: must be the name of this instance
    runTimeCallback: the callback function to monitor the status of simulation
    '''
    eispice.PyB.__init__(self, pNode, nNode, eispice.Voltage,\
                        self.i(name),eispice.Time)
    self.soc = initialSOC
    self.parameter = p
    self.capacity = 1.0*capacity/1000.0*3600.0 # convert to A.s
    K0,K1,K2,K3,K4=self.parameter
    self.voltage = K0+K1*self.soc+K2/self.soc+K3*np.log(self.soc)+K4*np.log(1-self.soc)
    self.time = 0.0
    self.runTimeCallback = runTimeCallback #runTimeCallback is a variable from passing parameter
    self.current = 0.0
    
  def model(self,i,t):
    i = float(i)
    t = float(t)
    if self.soc < 0.001: #prevent overflow
        self.voltage = 0.0
        self.soc = 0.0
        self.current = 0.0
        self.time = t
    else:
        K0,K1,K2,K3,K4=self.parameter
        deltaT = np.abs(t-self.time)
        cap = 1.0* self.capacity * self.soc + deltaT*i
        self.soc = float(cap)/self.capacity
        self.time = t
        self.current = i
        self.voltage = K0+K1*self.soc-K2/self.soc+K3*np.log(self.soc)+K4*np.log(1-self.soc)
    if self.runTimeCallback:
        try:
            self.runTimeCallback(self) # what does this mean
        except:
            debugString = "t:{time},v:{voltage},soc:{soc},i:{current}".format(**self.__dict__)
            print('\ncallback error:\n'+debugString)
    return self.voltage
    
class RealBattery(subckt.Subckt):
    '''
    1st-order/2nd-order RCBattery Model,consist with a OCV,a inner resistance,and one/two parallelized RC
    '''

    def __init__(self, pNode, nNode, batteryDescriptor):
        '''
        Arguments:
        pNode -- positive node name
        nNode -- negative node name
        parameterDict -- dictionary to describe the battery
        The following keys should be included:
        batteryDescriptor.Name = 'cell'
        batteryDescriptor.OCVParameter = OCV_SOC_Parameters
        batteryDescriptor.InnerR =  0.021
        batteryDescriptor.R1 = 0.045
        batteryDescriptor.C1 = 300
        batteryDescriptor.R2 = None
        batteryDescriptor.C2 = None
        batteryDescriptor.InitialSOC = 0.99
        batteryDescriptor.Capacity = 5300
        batteryDescriptor.OCVCallback = some call back function
        batteryDescriptor.BalanceResCallBack = None #if it's not None, then a balance resistance will be added.
            
        OCVParameter -- K0~K4 parameter of OCV-SOC relation
        InnerR -- Inner resistance of the battery
        R1,C1 -- R and C value of first order dynamic model
        '''
        name = batteryDescriptor.Name
        if batteryDescriptor.R2 is not None and batteryDescriptor.C2 is not None:
            self.C2 = [('C2_'+name,eispice.C('@nc2_'+name,pNode, batteryDescriptor.C2))]
            self.R2 = [('R2_'+name,eispice.R(pNode, '@nc2_'+name, batteryDescriptor.R2))]
            self.C1 = [('C1_'+name,eispice.C('@nc1_'+name,'@nc2_'+name, batteryDescriptor.C1))]
            self.R1 = [('R1_'+name,eispice.R('@nc2_'+name, '@nc1_'+name, batteryDescriptor.R1))]
        else:
            self.C1 = [('C1_'+name,eispice.C('@nc1_'+name,pNode, batteryDescriptor.C1))]
            self.R1 = [('R1_'+name,eispice.R(pNode, '@nc1_'+name, batteryDescriptor.R1))]
        self.iR = [('iR_'+name,eispice.R('@nc0_'+name, '@nc1_'+name, batteryDescriptor.InnerR))]
        self.ocv = [('OCV_'+name,OCV('@nc0_'+name,nNode,batteryDescriptor.OCVParameter,batteryDescriptor.InitialSOC,batteryDescriptor.Capacity,'OCV_'+name,batteryDescriptor.OCVCallback))]
        if batteryDescriptor.BalanceResCallBack is not None:
            self.balanceR = customizedCurrentSource(pNode,nNode, batteryDescriptor.BalanceResCallBack )
            
class RealBatteryGroup(subckt.Subckt):
    def __init__(self, pNode, nNode, descriptorList):
        '''
            Arguments:
            pNode -- positive node name
            nNode -- negative node name
            parameterDictList -- dictionary list to describe the batteries in the group
        '''
        batteries = []
        nameDict = {} #use a dict to make sure the battery name is not the same
        for i,des in enumerate(descriptorList):
            if des.Name in nameDict:
                des.Name = 'cell'+str(i)
            nameDict[des.Name] = des.Name
            pn = '@cellNode_'+str(i-1)
            nn = '@cellNode_'+str(i)
            if i == 0:
                pn = pNode
            if i == len(descriptorList) -1 :
                nn = nNode
            batteries+=RealBattery(pn,nn,des) #add a battery
        self.cells = batteries
        
class customizedCurrentSource(eispice.PyB):
  def __init__(self, pNode,nNode,runTimeCallback):
    '''
    runTimeCallback: the callback function to monitor the status of simulation
    '''
    eispice.PyB.__init__(self, pNode, nNode, eispice.Current,\
                            self.v(pNode),self.v(nNode),eispice.Time)
    self.time = 0.0
    self.runTimeCallback = runTimeCallback
    self.current = None
    self.vp = None
    self.vn = None
  def model(self,vp,vn,t):
    self.time = np.float(t)
    self.vp = np.float(vp)
    self.vn = np.float(vn)
    self.current = self.runTimeCallback(self)
    return self.current  
    
def printOCVInfo(device):
    '''
    A callback function to print the runtime status of the OCV device during simulation
    '''
    t = device.time
    if int(t)%40 ==0:  # print every 40 seconds
        debugString = "t:{time},v:{voltage},soc:{soc},i:{current}".format(**device.__dict__)
        print debugString
        
if __name__ == '__main__':
    #define a squre wave constant current load
    def constantCurrentLoad(load):
        if load.vp>load.vn:
            if load.time<1009:
                return 0.001
            elif load.time<1742:#int(load.time)%40 <10:
                return 2.652
            else:
                return 0.001
        else:
            return 0.001
    cct = eispice.Circuit("Real Battery Model Discharge test")
    #define a battery Cell with the pre-defined battery parameter
    cct.rb = RealBattery(1,eispice.GND,defaultDescriptor) #print the runtime message
    #define a customized load
    cct.load = customizedCurrentSource(1,eispice.GND,constantCurrentLoad) 
    #time step 1s, 3000s duration
    cct.tran('1', '3500') #timestep=1 last 25000 seconds
    eispice.plot(cct)
    
    
    
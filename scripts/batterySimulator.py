import eispice
from scipy import interpolate
import numpy as np
import matplotlib.pylab as plt
import serial
import time
import pickle

#chargeVoltage=[3.023, 3.398, 3.490, 3.557, 3.618, 3.656, 3.721, 3.846, 3.943, 4.057, 4.184]
#chargeQuantity=[74.2, 583, 1086.5, 1590.0, 2183.6, 2687.1, 3190.6, 3784.2, 4287.7, 4796.5, 5300.0]
chargeQuantity=[0,74.2,159,243.8,328.6,413.4,498.2,583,662.5,747.3,832.1\
               ,916.9,1001.7,1086.5,1171.3,1256.1,1340.9,1425.7,1505.2\
               ,1590,1674.8,1759.6,1844.4,1929.2,2014,2098.8,2183.6,2268.4\
               ,2347.9,2432.7,2517.5,2602.3,2687.1,2771.9,2856.7,2941.5\
               ,3026.3,3111.1,3190.6,3275.4,3360.2,3445,3529.8,3614.6\
               ,3699.4,3784.2,3869,3953.8,4033.3,4118.1,4202.9,4287.7\
               ,4372.5,4457.3,4542.1,4626.9,4711.7,4796.5,4876,4960.8\
               ,5045.6,5130.4,5215.2,5300]
chargeVoltage=[2.75,3.023,3.159,3.25,3.318,3.362,3.383,3.398,3.412,3.429,3.446\
              ,3.462,3.477,3.49,3.503,3.513,3.524,3.535,3.545,3.557,3.569\
              ,3.584,3.594,3.601,3.607,3.612,3.618,3.624,3.629,3.635,3.642\
              ,3.648,3.656,3.664,3.672,3.682,3.693,3.706,3.721,3.74,3.761\
              ,3.78,3.797,3.813,3.829,3.846,3.861,3.877,3.893,3.909,3.926\
              ,3.943,3.96,3.978,3.997,4.017,4.037,4.057,4.077,4.096,4.115\
              ,4.135,4.158,4.184]
              
class Battery(object):
    def __init__(self):
        global chargeVoltage
        global chargeQuantity
        self.intR = 0.0155  #initial resistance is 15.5mR
        self._qPoints = chargeQuantity
        self._vPoints =chargeVoltage
        self.qvCurveTck = interpolate.splrep(self._qPoints,self._vPoints,s=0.001) #use interpolate module to interpolate the QV curve
        #self.qVCurve = interpolate.interp1d(self._qPoints, self._vPoints)#relation of electric quantity and voltage
        self.voltage = 3.65
        self.current=0.0
        self._quantity = 5300 #corresponding voltage is 3.83V
        self.pNode = None
        self.nNode = None
        self.name = ''
        self.soc = 98.0
        self.cycles = 10
        self.balanceRate = 0.0
        
    @property
    def quantity(self):
        #Get the current quantity.
        return self._quantity

    @quantity.setter
    def quantity(self, newValue):
        self._quantity = newValue
        self.voltage = interpolate.splev( self._quantity ,self.qvCurveTck,der=0)
        return self._quantity,self.voltage
    
    def plotCVCurve(self):
        '''
        plot V curve according to Quantity
        '''
        fig= plt.figure()
        fig.suptitle('Q-V curve',fontsize=14,fontweight='bold')
        ax = fig.add_subplot(1,1,1)
        ax.set_xlabel('Voltage(V)')
        ax.set_ylabel('Quantity(mAh)')
        newX = np.arange(self._qPoints[0],self._qPoints[-1],0.1)
        newY = interpolate.splev(newX,self.qvCurveTck,der=0)
        ax.plot(self._qPoints,self._vPoints,'o',label='Quantity Points')
        ax.plot(newX,newY,'-',label='QV Curve')
        ax.legend(loc = 'lower right')
        plt.show()
        
class BatteryGroup(list):    
    # Battery group
    def __init__(self,arg):
        self.balanceResVal = 240
        self.voltageList = []
        self.currentList=[]
        self.quantityList = []
        self.socList = []
        self.cyclesList = []
        self.totalVoltage=0
        self.totalCurrent=0
        if isinstance(arg,int):
            count = arg
            self.length = count
            for i in range(count):
                b=Battery()
                b.pNode= 'V+'+ str(i)
                b.nNode= 'V-' + str(i)
                b.name = 'B'+str(i)
                self.append(b) #this make self list have actual element that is battery
        elif isinstance(arg,list):
            count = len(arg)
            self.length = countself
            for b in arg:
                self.append(b)
        for b in self:
            self.voltageList.append(b.voltage)
            self.currentList.append(b.current)
            self.quantityList.append(b.quantity)
            self.socList.append(b.soc)
            self.cyclesList.append(b.cycles)
            self.totalVoltage += b.voltage

        self.pNode = self[0].pNode # set the positive node of the first battery as the positive node of the battery group
        self.nNode = eispice.GND
        self.current = 0
        self.spiceModel = self.generateSpiceModel();
        
    def generateSpiceModel(self):
        self.spiceModel = [] #clear the spiceModel
        #setting up singel battery spice model
        for i in range(self.length-1):# in order to set the last battery sepratedly we should have self.length-1 here
            Vsp = ('V'+str(i),eispice.V(self[i].pNode,self[i].nNode,self[i].voltage))#eispice source model
            Rsp = ('iR'+str(i),eispice.R(self[i].nNode,self[i+1].pNode,self[i].intR))#eispice resistance model
            self.spiceModel.append(Vsp)
            self.spiceModel.append(Rsp) #set a signel battery spice model
            if self[i].balanceRate != 0.0:
                Rsb=('balance_'+ self[i].name,eispice.R(self[i].pNode,self[i+1].pNode, 1.0 * self.balanceResVal / self[i].balanceRate))
                self.spiceModel.append(Rsb)            
                
        # set the spice model for the last battery
        Vsp = ('V'+str(self.length-1),eispice.V(self[self.length-1].pNode,self[self.length-1].nNode,self[self.length-1].voltage))
        Rsp = ('iR'+str(self.length-1),eispice.R(self[self.length-1].nNode,self.nNode,self[self.length-1].intR))
        self.spiceModel.append(Vsp)
        self.spiceModel.append(Rsp)
        if self[self.length-1].balanceRate != 0.0:
             Rsb=('balance_'+ self[self.length-1].name,eispice.R(self[self.length-1].pNode,self.nNode, 1.0 * self.balanceResVal / self[self.length-1].balanceRate))
             self.spiceModel.append(Rsb) 
               
        for i in range(self.length):
            #self.voltageList[i] = round(self[i].voltage,3)
            #self.quantityList[i] = round(self[i].quantity,3)
            self.voltageList[i] = self[i].voltage
            self.quantityList[i] =self[i].quantity
            self.socList[i]  = round(self[i].soc,1)
            self.cyclesList[i]  = self[i].cycles
        self.totalCurrent=self[0].current
        self.totalVoltage=sum(self.voltageList)
        #having a new list to store all the battery spice models
        return self.spiceModel
    
class TimeMachine(object):
    NumberOfCells = 12
    NumberOfStacks = 2
    BATTERYCAPACITY=5300
    status = {
    'paused':False,\
    'totalCurrent':2.3,\
    'totalVoltage':0,\
    'voltageList':[],\
    'currentList':[],\
    'quantityList':[],\
    'socList':[],\
    'cyclesList':[],\
    }
                
    def __init__(self):
        self.timeStep = 1
        self.bg = BatteryGroup(self.NumberOfCells*self.NumberOfStacks)
        self.clock = 0.0 #second
        self.load = 96 # 32 the load  of discharge is 32R 
        self.source=2.65 # the current of the charge source 2.65A
        self.updateInfo()
        self.revert() #try to revert to last status
        
    def updateInfo(self):
        self.status['voltageList'] = self.bg.voltageList
        self.status['currentList'] = self.bg.currentList
        self.status['quantityList'] = self.bg.quantityList
        self.status['socList'] = self.bg.socList
        self.status['cyclesList'] = self.bg.cyclesList
        self.status['totalVoltage']=self.bg.totalVoltage
        self.status['totalCurrent']=self.bg.totalCurrent
    
    def discharge(self,time,saveStatus = True):
        totalQuantity=0
        totalSOC=0
        f=open('dischargeData.txt','a')
        cct = eispice.Circuit("battery stimulator discharge")
        cct.batteries = self.bg.generateSpiceModel();#it will return a list contains connected batteries
        cct.load = eispice.R(self.bg.pNode,self.bg.nNode,self.load)# put the load on
        cct.tran('0.01n','0.02n')#doing transient analysis 
        for i in range(self.NumberOfCells*self.NumberOfStacks):
            self.bg[i].current=abs(cct.i['V'+str(i)]('0.01n')) * 1000      
            self.bg[i].quantity -= self.bg[i].current * time/3600
            self.bg[i].soc= self.bg[i].quantity/self.BATTERYCAPACITY
            totalQuantity += self.bg[i].quantity
        #print 'the total quantity is:',totalQuantity 
        totalSOC=totalQuantity/(self.BATTERYCAPACITY*self.NumberOfCells*self.NumberOfStacks)
        self.clock += time
        f.write(str(self.clock)+'\t')
        f.write(str(totalSOC)+'\t')
        f.write('\n')
        f.close()
        if saveStatus:
             self.backup() # save current status
        self.updateInfo()
       
    def charge(self,time,saveStatus = True):       
        cct = eispice.Circuit("battery stimulator charge")
        cct.batteries = self.bg.generateSpiceModel();
        cct.source = eispice.I(self.bg.pNode,self.bg.nNode,self.source)# constant current charge source
        cct.tran('0.01n','0.02n')#doing transient analysis
        for i in range(self.NumberOfCells*self.NumberOfStacks):
            self.bg[i].current=abs(cct.i['V'+str(i)]('0.01n')) * 1000     
            self.bg[i].quantity += self.bg[i].current * time / 3600
            self.bg[i].soc = self.bg[i].quantity /self.BATTERYCAPACITY *100
            print('current:{0},  quantity is:{1}'.format(self.bg[i].current,self.bg[i].quantity))
        self.clock += time
        if saveStatus:
             self.backup() # save current status
        self.updateInfo()
             
    def batteryBalance(self,time,saveStatus=True):
        cct = eispice.Circuit("battery stimulator doing balance")
        cct.batteries = self.bg.generateSpiceModel();#it will return a list contains connected batteries
        cct.tran('0.01n','0.02n')#doing transient analysis 
        for i in range(self.NumberOfCells*self.NumberOfStacks):
            self.bg[i].current=abs(cct.i['V'+str(i)]('0.01n'))*1000   #uint is mA       
            self.bg[i].quantity -= self.bg[i].current * time/3600 #uint is mAh
            #print('current:{0},quantity is:{1}'.format(self.bg[i].current,self.bg[i].quantity))
        self.clock += time
        if saveStatus:
            self.backup() # save current status
        self.updateInfo()
             
    def chargeNdischarge(self,time,saveStatus = True ):        
        cct = eispice.Circuit("battery stimulator charge")
        cct.batteries = self.bg.generateSpiceModel();
        cct.source = eispice.I(self.bg.pNode,self.bg.nNode,self.source)# constant current charge source
        cct.load = eispice.R(self.bg.pNode,self.bg.nNode,self.load)# put the load on
        cct.tran('0.01n','0.02n')#doing transient analysis 
        for i in range(self.NumberOfCells*self.NumberOfStacks):
            self.bg[i].current=cct.i['V'+str(i)]('0.01n')*1000    
            self.bg[i].quantity += self.bg[i].current * time /3600
            print('current:{0},  quantity Gain:{1}'.format(self.bg[i].current,self.bg[i].qGain))
        if saveStatus:
             self.backup() # save current status
        self.updateInfo()
            
    def backup(self,fileName = 'currentStatus.pickle'):
        '''
        backup the battery group status to a pickle file
        '''
        bl = []
        for b in self.bg:
            bl.append(b)
        allData = {}
        allData['batteryGroup'] = bl
        allData['clock'] = self.clock
        allData['load'] = self.load
        allData['source'] = self.source
        try:
            pickle.dump(allData,open(fileName,'w'))
            return True
        except:
            print('error when permanenting the battery group!')
            return False
               
    def revert(self,fileName = 'currentStatus.pickle'):
        '''
        revert the battery group status from a pickle file
        '''
        try:
            self.bg.generateSpiceModel()
            allData = pickle.load(open(fileName,'r'))
            if isinstance(allData,dict):
                bgt = BatteryGroup(allData['batteryGroup'])
                del self.bg
                self.bg =bgt               
                self.clock = allData['clock'] #second
                self.load = allData['load']
                self.source= allData['source']
                self.status['voltageList'] = self.bg.voltageList
                self.status['currentList'] = self.bg.currentList
                self.status['quantityList'] = self.bg.quantityList
                self.status['socList'] = self.bg.socList
                self.status['cyclesList'] = self.bg.cyclesList
                self.status['totalVoltage']=self.bg.totalVoltage
                self.status['totalCurrent']=self.bg.totalCurrent
            else:
                return False
            return True
        except:
            print('error when load battery group from file!')
            return False
                    
    def goto(self,time,mode,saveStatus = True):
        elapseTime = time - self.clock
        if mode == 'discharge':
            for time in range(int(elapseTime/self.timeStep)): #simulate the time in smaller steps
                self.discharge(self.timeStep,False)
            if saveStatus:
                self.backup() # save current status
        elif mode == 'charge':
            for time in range(int(elapseTime/self.timeStep)): #simulate the time in smaller steps
                self.charge(self.timeStep,False)
            if saveStatus:
                self.backup() # save current status
        else:
            print('please input correct mode(charge/discharge) in your function.')
        self.updateInfo()
               
    def testSpiceModle(self):
        #calculate the current
        for b in self.bg:
            b.balanceRate=1.0
            b.intR=0.0155
            b._quantity = 5300
        cct = eispice.Circuit("battery stimulator not discharge not charge")
        cct.batteries = self.bg.generateSpiceModel();#it will return a list contains connected batteries
        cct.tran('0.01n','0.02n')#doing transient analysis
        for i in range(self.NumberOfCells*self.NumberOfStacks):
            print cct.i['V'+str(i)]('0.01n')
        self.updateInfo()
            
    def drawCircuit(self):
        import networkx as nx
        import matplotlib.pyplot as plt
        model = self.bg.generateSpiceModel()
        G = nx.Graph()
        for name,device in model:
            G.add_node(device.node[0],color = 'green')
            G.add_node(device.node[1],color = 'green')
            G.add_edge(device.node[0],device.node[1])
            print name,device.node
        nx.draw(G)
        plt.show()
    
"""
if __name__ == "__main__":
    np.set_printoptions(threshold='nan')
    tm = TimeMachine()
    b=Battery()
    b.plotCVCurve()
"""    



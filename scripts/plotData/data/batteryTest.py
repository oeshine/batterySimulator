import eispice

class Battery(object):
    def __init__(self):
        self.intR = 0.0155  #initial resistance is 15.5mR
        self.voltage = 3.65
        self.pNode = None
        self.nNode = None
        self.name = ''
        self.balanceRate = 1.0

class BatteryGroup(list):    
    # Battery group
    def __init__(self,arg):
        self.balanceResVal = 240
        self.voltageList = []
        for i in range(count):
                b=Battery()
                b.pNode='V+'+ str(i)
                b.nNode='V-' + str(i)
                b.name = 'B'+str(i)
                self.append(b) #this make self list have actual element that is battery
        
        for b in self:
            self.voltageList.append(b.voltage)
           
        self.pNode = self[0].pNode # set the positive node of the first battery as the positive node of the battery group
        self.nNode = eispice.GND
        self.spiceModel = self.generateSpiceModel();
        
    def generateSpiceModel(self):
        self.spiceModel = [] #clear the spiceModel
        #setting up singel battery spice model
        for i in range(self.length-1):# in order to set the last battery sepratedly we should have self.length-1 here
            Vsp = ('V'+str(i),eispice.V(self[i].pNode,self[i].nNode,self[i].voltage))#eispice source model
            Rsp = ('iR'+str(i),eispice.R(self[i].nNode,self[i+1].pNode,self[i].intR))#eispice resistance model
            self.spiceModel.append(Vsp)
            self.spiceModel.append(Rsp) #set a signel battery spice model

        # set the spice model for the last battery
        Vsp = ('V'+str(self.length-1),eispice.V(self[self.length-1].pNode,self[self.length-1].nNode,self[self.length-1].voltage))
        Rsp = ('iR'+str(self.length-1),eispice.R(self[self.length-1].nNode,self.nNode,self[self.length-1].intR))
        self.spiceModel.append(Vsp)
        self.spiceModel.append(Rsp)
        
        for b in self:
            if b.balanceRate != 0.0:
                Rsb=('balance_'+ b.name,eispice.R(b.pNode,b.intR, 1.0* self.balanceResVal/b.balanceRate))
                self.spiceModel.append(Rsb)
        
        for i in range(self.length):
            self.voltageList[i] = round(self[i].voltage,3)

        return self.spiceModel

class TimeMachine(object):
    NumberOfCells = 2
    NumberOfStacks = 1
    status = {
    'paused':False,\
    'totalCurrent':2.3,\
    'totalVoltage':412,\
    'voltageList':[],\
    'quantityList':[],\
    'healthList':[],\
    'cyclesList':[],\
    }
                
    def __init__(self):
        self.timeStep = 1
        self.bg = BatteryGroup(self.NumberOfCells*self.NumberOfStacks)
        self.clock = 0.0 #second
        self.load = 32 # 32 the load  of discharge is 32R 
        self.source=2.65 # the current of the charge source 2.65A
        self.status['voltageList'] = self.bg.voltageList
        
        self.revert() #try to revert to last status
    
    def NdischargeNCharge(self,time,saveStatus=True):
        #calculate the current
        cct = eispice.Circuit("battery stimulator not discharge not charge")
        cct.batteries = self.bg.generateSpiceModel();#it will return a list contains connected batteries
        cct.load = eispice.R(self.bg.pNode,self.bg.nNode,10000000)
        cct.tran('0.01n','0.02n')#doing transient analysis 
        for i in range(self.NumberOfCells*self.NumberOfStacks):
            print cct.i['V'+str(i)]('0.01n')
            self.bg.current=self.bg.current+abs(cct.i['V'+str(i)]('0.01n'))
        print self.bg.current
       
        qLoss = self.bg.current * time
        for b in self.bg:
            b.quantity = b.quantity - qLoss
        print('current:{0},  quantity loss:{1}'.format(self.bg.current,qLoss))

        
if __name__ == "__main__":
    np.set_printoptions(threshold='nan')
    tm = TimeMachine()
    tm.NdischargeNCharge(1)

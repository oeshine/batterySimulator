import eispice
cct = eispice.Circuit("battery stimulator not discharge not charge")
def generateSpiceModel():
    spiceModel=[]
    
    Vsp = ('Vsp',eispice.V('V1+',eispice.GND,3.65))#eispice source model
    Rsp = ('Rsp',eispice.R('V1+','V2-',0.0155))#eispice resistance model
    Rb=('Rb',eispice.R('V2-',eispice.GND,240))
    
    Vsp2=('Vsp2',eispice.V('V2-','V2+',3.65))
    Rsp2=('Rsp2',eispice.R('V2+','V3-',0.0155))
    Rb2=('Rb2',eispice.R('V2-','V3-',240))
    
    Vsp3=('Vsp3',eispice.V('V3-','V3+',3.65))
    Rsp3=('Rsp3',eispice.R('V3+','V4-',0.0155))
    Rb3=('Rb3',eispice.R('V3-','V4-',240))
    
    load=('load',eispice.R('V4-',eispice.GND,1000))
    
    spiceModel.append(Vsp)
    spiceModel.append(Rsp) #set a signel battery spice model
    spiceModel.append(Rb)
    
    spiceModel.append(Vsp2)
    spiceModel.append(Rsp2)
    spiceModel.append(Rb2)
    
    spiceModel.append(Vsp3)
    spiceModel.append(Rsp3)
    spiceModel.append(Rb3)
   
    spiceModel.append(load)
    return spiceModel
    
cct.batteries = generateSpiceModel();
cct.tran('0.01n','0.02n')
print 'current of Vsp is:', cct.i['Vsp']('0.01n') #unit is A
print 'current of Vsp2 is:', cct.i['Vsp2']('0.01n') #unit is A
print 'current of Vsp3 is:', cct.i['Vsp3']('0.01n') #unit is A

"""result
current of Vsp is: 78.4743471877
current of Vsp2 is: -78.50476189
current of Vsp3 is: -78.50476189
"""
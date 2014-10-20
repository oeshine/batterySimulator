import eispice
cct = eispice.Circuit("battery stimulator not discharge not charge")
def generateSpiceModel():
    spiceModel=[]
    
    Vsp = ('Vsp',eispice.V('V1+',eispice.GND,3.65))#eispice source model
    Rsp = ('Rsp',eispice.R('V1+','V2-',0.0155))#eispice resistance model
    Rb=('Rb',eispice.R('V2-',eispice.GND,240))
    
    Vsp2=('Vsp2',eispice.V('V2-','V2+',3.65))
    Rsp2=('Rsp2',eispice.R('V2+',eispice.GND,0.0155))
    Rb2=('Rb2',eispice.R('V2-',eispice.GND,240))
    
    spiceModel.append(Vsp)
    spiceModel.append(Rsp) #set a signel battery spice model
    spiceModel.append(Rb)
    
    spiceModel.append(Vsp2)
    spiceModel.append(Rsp2)
    spiceModel.append(Rb2)

    return spiceModel
    
cct.batteries = generateSpiceModel();
cct.tran('0.01n','0.02n')
print 'current of Vsp is:', cct.i['Vsp']('0.01n') #unit is A
print 'current of Vsp2 is:', cct.i['Vsp2']('0.01n') #unit is A

"""reslut
current of Vsp is: -0.0152073511919
current of Vsp2 is: -0.0152073511919
"""
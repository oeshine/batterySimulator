import eispice

cct = eispice.Circuit("battery stimulator not discharge not charge")
cct.Vsource1=eispice.V('V1+',eispice.GND,3.65)
cct.intR1=eispice.R('V1+','intR1',0.0155)
cct.balanceR1=eispice.R('intR1',eispice.GND,240)

cct.tran('0.01n','0.02n')
print 'current of Vsource1 is:', cct.i['Vsource1']('0.01n') #unit is A
print 'voltage of V1+ is:',cct.v['V1+']('0.01n') #unit is V

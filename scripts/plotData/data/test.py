if __name__ == '__main__':
    strV=[]
    strT=[]
    strF=[]
    for stackNumber in range(8):
        for cellNumber in range(12):
            if(cellNumber<10):
                strV.append('V'+str(stackNumber)+'0'+str(cellNumber))
            else:
                strV.append('V'+str(stackNumber)+str(cellNumber))
    print strV
    
    for stackNumber in range(8):
        for cellNumber in range(2):
             strT.append('T'+str(stackNumber)+'0'+str(cellNumber))
    print strT
    
    for stackNumber in range(8):
        for cellNumber in range(3):
            strF.append('V'+str(stackNumber)+'0'+str(cellNumber))
    print strF
            
                
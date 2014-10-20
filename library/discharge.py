print('Now discharging')
for i in range(1000):
    tm.discharge(1) #0.1s
    if quitFlag:
        print('quit signal captured!')
        break
print('done!')
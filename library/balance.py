print('Now batteryBalance')
for i in range(40000):
    tm.batteryBalance(1) #0.1s
    if quitFlag:
        print('quit signal captured!')
        break
print('done!')
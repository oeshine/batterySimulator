print('Now charging')
for i in range(1000):
    tm.charge(1)
    if quitFlag:
        print('quit signal captured!')
        break
print('done!')
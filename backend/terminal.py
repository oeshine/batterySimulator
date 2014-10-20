import os
import argparse
from serial_manager import SerialManager
SERIAL_PORT = 'COM11'
BITSPERSECOND = 9600

### Setup Argument Parser
argparser = argparse.ArgumentParser(description='Run TS_BatterySimulator.', prog='TS_BatterySimulator')
argparser.add_argument('port', metavar='serial_port', nargs='?', default=False,
                    help='serial port to the Simulator')
args = argparser.parse_args()
if not SERIAL_PORT:
    if args.port:
        # (1) get the serial device from the argument list
        SERIAL_PORT = args.port
        print "Using serial device '"+ SERIAL_PORT +"' from command line."
    else:
        print 'Please select a serialport via args'
if os.name == 'nt': #sys.platform == 'win32': 
    GUESS_PREFIX = "Arduino"   
elif os.name == 'posix':
    if sys.platform == "linux" or sys.platform == "linux2":
        GUESS_PREFIX = "2341"  # match by arduino VID
    else:
        GUESS_PREFIX = "tty.usbmodem"    
else:
    GUESS_PREFIX = "no prefix"   
    
if __name__ == '__main__':
    #if not SERIAL_PORT:
    #    SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)

    SerialManager.connect(SERIAL_PORT, BITSPERSECOND)
    while SerialManager.is_connected():
        command = raw_input("Input your command>>>")
        if len(command) != 0:
            SerialManager.read_existing() #clear rx_buffer
            if SerialManager.write( command+'\r'):
                str = SerialManager.read_to('\r')
                print(str)
            else:
                print("write error!")
                break
    print("Port closed!")




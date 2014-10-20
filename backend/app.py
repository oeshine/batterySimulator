import threading
import sys, os, time
import glob, json, argparse, copy
import socket, webbrowser
from wsgiref.simple_server import WSGIRequestHandler, make_server
from bottle import *
from serial_manager import SerialManager
from batterySimulator import TimeMachine

waitEvent = threading.Event()

tm = TimeMachine()

APPNAME = "TS_BatterySimulator"
VERSION = "0.1"
COMPANY_NAME = "com.bhl"
SERIAL_PORT = None #'COM1'
BITSPERSECOND = 9600
NETWORK_PORT = 4567
HARDWARE = 'x86'  # also: 'beaglebone', 'raspberrypi'
CONFIG_FILE = "TS_BatterySimulator.conf"
GUESS_PREFIX = "no prefix"    


graphDataLengthMax =128  #default max data length of the graph

pct = 0
quitFlag = False

def parseLines(f):
    pySegs = []
    for line in f:
        if len(line.strip()) <=0:
            continue
        if line[0] != ' ' and line[0] !='\t':
            if line != '':
                pySegs.append(line)
        else:
            pySegs[-1] = pySegs[-1] + line
    return pySegs
    
def CommandProcessor(e):
    '''
    execute command lines from webgui
    '''
    global pct,quitFlag
    while True:
        tm.status['paused'] = True
        print('Waiting for event to start..')
        event_is_set = e.wait()
        tm.status['paused'] = False
        print('Running...')
        try:
            f = open('currentCommandList.py','r')
            lines = parseLines(f)
            totalCount = len(lines)
            f.close()
            for i,line in enumerate(lines):
                try:
                    exec(line)
                except:
                    print('error in line:%s'%line)
                pct = int((1.0+i)/totalCount * 100)
                print('exec percentage: ' + str(pct) + '%')
                e.wait()
                if quitFlag:
                    print('quit signal captured!')
                    break
            pct = 100
            quitFlag = True
        except:
            print('error in exec')
        print('command ended!')
        e.clear()
        
        
def serialProcessor():
    global quitFlag
    RelayStatus=0
    '''
        process serial command and send response.
        'V'         // UART-command for receiving
        'T'         //UART-command for read temperature
        'F'	        //UART-command for read flag
        'R'		    //UART-command for read total voltage
        'I' 		//UART-command for  read total current
        'C' 		//UART-command for close the relay
        'O' 		//UART-command for open the relay
        'P'		    //UART-command for receiving the PWM rate
        'J'         //UART-command for read time
        'K'         //UART-command for kill the simulation
    '''   
    
    while True:
        try:
            chars = SerialManager.read_to('\r')
            if len(chars) > 0:
                print('Processing Command:' + chars)
                stackNum = int(chars[1])
                cellNum = int(chars[2:4])
                #cellNum=int(chars[2])*10 + int(chars[3])
                index = stackNum*tm.NumberOfCells+cellNum
                #print "stackNum %d, cellNum %d, index %d" %(stackNum,cellNum,index)
                if chars[0] == 'V':
                    SerialManager.write(str(tm.status['voltageList'][index])+ '\r')
                elif chars[0] == 'B':
                    tm.bg[index].balanceRate = 1.0 * int(chars[4:])/100.0
                    #print 'balcenRate is:', tm.bg[index].balanceRate
                elif chars[0] == 'T':
                    SerialManager.write(str(0)+ '\r')
                elif chars[0] == 'R':
                    totalVoltage=sum(tm.status['voltageList'][:])
                    SerialManager.write(str(totalVoltage)+ '\r')
                elif chars[0] == 'I':
                    totalCurrent=sum(tm.status['voltageList'][:])/tm.load
                    SerialManager.write(str(totalCurrent)+ '\r')
                elif chars[0] == 'C':
                    RelayStatus=1
                    SerialManager.write(str(RelayStatus)+ '\r')
                elif chars[0] == 'O':
                    RelayStatus=0
                    SerialManager.write(str(RelayStatus)+ '\r')
                elif chars[0] == 'J':
                    SerialManager.write(str(tm.clock)+ '\r')
                elif chars[0] == 'K':
                    quitFlag = True
                else:
                    print 'Command Not Defined'
                    SerialManager.write('Command Not Defined'+ '\r')
            time.sleep(0.08)
        except:
            print("error when processing command")
            time.sleep(0.1)
    
def resources_dir():
    """This is to be used with all relative file access.
       _MEIPASS is a special location for data files when creating
       standalone, single file python apps with pyInstaller.
       Standalone is created by calling from 'other' directory:
       python pyinstaller/pyinstaller.py --onefile app.spec
    """
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        # root is one up from this file
        return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
                
def storage_dir():
    directory = ""
    if sys.platform == 'darwin':
        # from AppKit import NSSearchPathForDirectoriesInDomains
        # # NSApplicationSupportDirectory = 14
        # # NSUserDomainMask = 1
        # # True for expanding the tilde into a fully qualified path
        # appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME)
        directory = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', COMPANY_NAME, APPNAME)
    elif sys.platform == 'win32':
        directory = os.path.join(os.path.expandvars('%APPDATA%'), COMPANY_NAME, APPNAME)#C:\Users\oeshine\AppData\Roaming\com.bhl
    else:
        directory = os.path.join(os.path.expanduser('~'), "." + APPNAME)
        
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    return directory

class HackedWSGIRequestHandler(WSGIRequestHandler):
    """ This is a heck to solve super slow request handling
    on the BeagleBone and RaspberryPi. The problem is WSGIRequestHandler
    which does a reverse lookup on every request calling gethostbyaddr.
    For some reason this is super slow when connected to the LAN.
    (adding the the IP and name of the requester in the /etc/hosts file
    solves the problem but obviously is not practical)
    """
    def address_string(self):
        """Instead of calling getfqdn -> gethostbyaddr we ignore."""
        # return "(a requester)"
        return str(self.client_address[0])

def run_with_callback(host, port):
    """ Start a wsgiref server instance with control over the main loop.
        This is a function that I derived from the bottle.py run()
    """
    handler = default_app()
    server = make_server(host, port, handler, handler_class=HackedWSGIRequestHandler)
    server.timeout = 0.01
    server.quiet = True
    print "Persistent storage root is: " + storage_dir()
    print "-----------------------------------------------------------------------------"
    print "Bottle server starting up ..."
    print "Serial is set to %d bps" % BITSPERSECOND
    print "Point your browser to: "    
    print "http://%s:%d/      (local)" % ('127.0.0.1', port)  
    # if host == '':
    #     try:
    #         print "http://%s:%d/   (public)" % (socket.gethostbyname(socket.gethostname()), port)
    #     except socket.gaierror:
    #         # print "http://beaglebone.local:4444/      (public)"
    #         pass
    print "Use Ctrl-C to quit."
    print "-----------------------------------------------------------------------------"    
    print
    # auto-connect on startup
    global SERIAL_PORT
    if not SERIAL_PORT:
        SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)
    SerialManager.connect(SERIAL_PORT, BITSPERSECOND)
    # open web-browser
    try:
        webbrowser.open_new_tab('http://127.0.0.1:'+str(port))
        pass
    except webbrowser.Error:
        print "Cannot open Webbrowser, please do so manually."
    sys.stdout.flush()  # make sure everything gets flushed
    while 1:
        try:
            server.handle_request()
            #tm.run()
        except KeyboardInterrupt:
            break
    print "\nShutting down..."
    SerialManager.close()

@route('/hello')
def hello_handler():
    return "Hello World!!"

@route('/css/:path#.+#')
def static_css_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/css'))
    
@route('/js/:path#.+#')
def static_js_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/js'))
    
@route('/img/:path#.+#')
def static_img_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/img'))

@route('/favicon.ico')
def favicon_handler():
    return static_file('favicon.ico', root=os.path.join(resources_dir(), 'frontend/img'))
    

### LIBRARY

@route('/library/get/:path#.+#')
def static_library_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'library'), mimetype='text/plain')
    
@route('/library/list')
def library_list_handler():
    # return a json list of file names
    file_list = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(os.path.join(resources_dir(), 'library'))
        file_list = glob.glob('*')
    finally:
        os.chdir(cwd_temp)
    return json.dumps(file_list)

### QUEUE

def encode_filename(name):
    str(time.time()) + '-' + base64.urlsafe_b64encode(name)
    
def decode_filename(name):
    index = name.find('-')
    return base64.urlsafe_b64decode(name[index+1:])
    

@route('/queue/get/:name#.+#')
def static_queue_handler(name): 
    return static_file(name, root=storage_dir(), mimetype='text/plain')

@route('/queue/list')
def library_list_handler():
    # base64.urlsafe_b64encode()
    # base64.urlsafe_b64decode()
    # return a json list of file names
    files = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(storage_dir())
        files = filter(os.path.isfile, glob.glob("*"))
        files.sort(key=lambda x: os.path.getmtime(x))
    finally:
        os.chdir(cwd_temp)
    return json.dumps(files)
    
@route('/queue/save', method='POST')
def queue_save_handler():
    ret = '0'
    if 'command_list_name' in request.forms and 'command_program' in request.forms:
        name = request.forms.get('command_list_name')
        command_program = request.forms.get('command_program')
        filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
        if os.path.exists(filename) or os.path.exists(filename+'.starred'):
            return "file_exists"
        try:
            fp = open(filename, 'w')
            fp.write(command_program)
            print "file saved: " + filename
            ret = '1'
        finally:
            fp.close()
    else:
        print "error: save failed, invalid POST request"
    return ret

@route('/queue/rm/:name')
def queue_rm_handler(name):
    # delete gcode item, on success return '1'
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename):
            try:
                os.remove(filename);
                print "file deleted: " + filename
                ret = '1'
            finally:
                pass
    return ret   
    
@route('/queue/star/:name')
def queue_star_handler(name):
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename):
            os.rename(filename, filename + '.starred')
            ret = '1'
    return ret

@route('/queue/unstar/:name')
def queue_unstar_handler(name):
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename + '.starred'):
            os.rename(filename + '.starred', filename)
            ret = '1'
    return ret 

    

@route('/')
@route('/index.html')
@route('/app.html')
def default_handler():
    return static_file('app.html', root=os.path.join(resources_dir(), 'frontend') )

@route('/canvas')
def canvas_handler():
    return static_file('testCanvas.html', root=os.path.join(resources_dir(), 'frontend'))    

@route('/serial/:connect')
def serial_handler(connect):
    if connect == '1':
        # print 'js is asking to connect serial'      
        if not SerialManager.is_connected():
            try:
                global SERIAL_PORT, BITSPERSECOND, GUESS_PREFIX
                if not SERIAL_PORT:
                    SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)
                SerialManager.connect(SERIAL_PORT, BITSPERSECOND)
                ret = "Serial connected to %s:%d." % (SERIAL_PORT, BITSPERSECOND)  + '<br>'
                time.sleep(1.0) # allow some time to receive a prompt/welcome
                SerialManager.flush_input()
                SerialManager.flush_output()
                return ret
            except serial.SerialException:
                SERIAL_PORT = None
                print "Failed to connect to serial."    
                return ""          
    elif connect == '0':
        # print 'js is asking to close serial'    
        if SerialManager.is_connected():
            if SerialManager.close(): return "1"
            else: return ""  
    elif connect == "2":
        # print 'js is asking if serial connected'
        if SerialManager.is_connected(): return "1"
        else: return ""
    else:
        print 'ambigious connect request from js: ' + connect            
        return ""

@route('/status')
def get_status():
    status = copy.deepcopy(tm.status)
    status['serial_connected'] = SerialManager.is_connected()
    return json.dumps(status)

@route('/pause/:flag')
def set_pause(flag):
    global quitFlag
    if flag == '1':
        quitFlag = False
        waitEvent.clear()
    elif flag == '0':
        quitFlag = False
        waitEvent.set()
    return flag
@route('/reset')
def reset_handler():
    return '1'

@route('/stop')
def reset_handler():
    global quitFlag
    quitFlag = True
    #waitEvent.set()
    return 'Stop flag setted!'

@route('/gcode', method='POST')
def gcode_submit_handler():
    global pct,quitFlag
    command_program = request.forms.get('command_program')
    if command_program:
        try:
            f = open('currentCommandList.py','w')
            f.write(command_program)
            pct = 0
            quitFlag = False
            waitEvent.set() #start command processor
            return "__ok__"
        except:
            return "write error!"
    else:
        return "disconnected"

@route('/queue_pct_done')
def queue_pct_done_handler():
    global pct,quitFlag
    if quitFlag:
        return None
    return str(pct)
    
@route('/graph_data_length_max')
def graph_data_length_max_handler():
    return str(graphDataLengthMax)

@route('/svg_reader', method='POST')
def svg_upload():
    """Parse SVG string."""
    filename = request.forms.get('filename')
    filedata = request.forms.get('filedata')

    if filename and filedata:
        print "You uploaded %s (%d bytes)." % (filename, len(filedata))
        #if filename[-4:] in ['.dxf', '.DXF']: 
        #    res = read_dxf(filedata, TOLERANCE, optimize)
        #else:
        #    res = read_svg(filedata, [1220,610], TOLERANCE, dpi_forced, optimize)
        # print boundarys
        jsondata = json.dumps({})
        # print "returning %d items as %d bytes." % (len(res['boundarys']), len(jsondata))
        return jsondata
    return "You missed a field."

       
### Setup Argument Parser
argparser = argparse.ArgumentParser(description='Run TS_BatterySimulator.', prog='TS_BatterySimulator')
argparser.add_argument('port', metavar='serial_port', nargs='?', default=False,
                    help='serial port to the Simulator')
argparser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
argparser.add_argument('-p', '--public', dest='host_on_all_interfaces', action='store_true',
                    default=False, help='bind to all network devices (default: bind to 127.0.0.1)')
argparser.add_argument('-l', '--list', dest='list_serial_devices', action='store_true',
                    default=False, help='list all serial devices currently connected')
argparser.add_argument('-d', '--debug', dest='debug', action='store_true',
                    default=False, help='print more verbose for debugging')
argparser.add_argument('--beaglebone', dest='beaglebone', action='store_true',
                    default=False, help='use this for running on beaglebone')
argparser.add_argument('--raspberrypi', dest='raspberrypi', action='store_true',
                    default=False, help='use this for running on Raspberry Pi')
argparser.add_argument('-m', '--match', dest='match',
                    default=GUESS_PREFIX, help='match serial device with this string')                                        
args = argparser.parse_args()



print "TS_BatterySimulator " + VERSION

if args.beaglebone:
    HARDWARE = 'beaglebone'
    NETWORK_PORT = 80
    ### if running on beaglebone, setup (pin muxing) and use UART1
    # for details see: http://www.nathandumont.com/node/250
    SERIAL_PORT = "/dev/ttyO1"
    # echo 0 > /sys/kernel/debug/omap_mux/uart1_txd
    fw = file("/sys/kernel/debug/omap_mux/uart1_txd", "w")
    fw.write("%X" % (0))
    fw.close()
    # echo 20 > /sys/kernel/debug/omap_mux/uart1_rxd
    fw = file("/sys/kernel/debug/omap_mux/uart1_rxd", "w")
    fw.write("%X" % ((1 << 5) | 0))
    fw.close()

    ### Set up atmega328 reset control
    # The reset pin is connected to GPIO2_7 (2*32+7 = 71).
    # Setting it to low triggers a reset.
    # echo 71 > /sys/class/gpio/export
    try:
        fw = file("/sys/class/gpio/export", "w")
        fw.write("%d" % (71))
        fw.close()
    except IOError:
        # probably already exported
        pass
    # set the gpio pin to output
    # echo out > /sys/class/gpio/gpio71/direction
    fw = file("/sys/class/gpio/gpio71/direction", "w")
    fw.write("out")
    fw.close()
    # set the gpio pin high
    # echo 1 > /sys/class/gpio/gpio71/value
    fw = file("/sys/class/gpio/gpio71/value", "w")
    fw.write("1")
    fw.flush()
    fw.close()

    ### read stepper driver configure pin GPIO2_12 (2*32+12 = 76).
    # Low means Geckos, high means SMC11s
    try:
        fw = file("/sys/class/gpio/export", "w")
        fw.write("%d" % (76))
        fw.close()
    except IOError:
        # probably already exported
        pass
    # set the gpio pin to input
    fw = file("/sys/class/gpio/gpio76/direction", "w")
    fw.write("in")
    fw.close()
    # set the gpio pin high
    fw = file("/sys/class/gpio/gpio76/value", "r")
    ret = fw.read()
    fw.close()
    print "Stepper driver configure pin is: " + str(ret)

elif args.raspberrypi:
    HARDWARE = 'raspberrypi'
    NETWORK_PORT = 80
    SERIAL_PORT = "/dev/ttyAMA0"
    import RPi.GPIO as GPIO
    # GPIO.setwarnings(False) # surpress warnings
    GPIO.setmode(GPIO.BCM)  # use chip pin number
    pinSense = 7
    pinReset = 2
    pinExt1 = 3
    pinExt2 = 4
    pinExt3 = 17
    pinTX = 14
    pinRX = 15
    # read sens pin
    GPIO.setup(pinSense, GPIO.IN)
    isSMC11 = GPIO.input(pinSense)
    # atmega reset pin
    GPIO.setup(pinReset, GPIO.OUT)
    GPIO.output(pinReset, GPIO.HIGH)
    # no need to setup the serial pins
    # although /boot/cmdline.txt and /etc/inittab needs
    # to be edited to deactivate the serial terminal login
    # (basically anything related to ttyAMA0)

if args.list_serial_devices:
    SerialManager.list_devices(BITSPERSECOND)
else:
    if not SERIAL_PORT:
        if args.port:
            # (1) get the serial device from the argument list
            SERIAL_PORT = args.port
            print "Using serial device '"+ SERIAL_PORT +"' from command line."
        else:
            # (2) get the serial device from the config file        
            if os.path.isfile(CONFIG_FILE):
                fp = open(CONFIG_FILE)
                line = fp.readline().strip()
                if len(line) > 3:
                    SERIAL_PORT = line
                    print "Using serial device '"+ SERIAL_PORT +"' from '" + CONFIG_FILE + "'."

    if not SERIAL_PORT:
        if args.match:
            GUESS_PREFIX = args.match
            SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)
            if SERIAL_PORT:
                print "Using serial device '"+ str(SERIAL_PORT)
                if os.name == 'posix':
                    # not for windows for now
                    print "(first device to match: " + args.match + ")"            
        else:
            SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)
            if SERIAL_PORT:
                print "Using serial device '"+ str(SERIAL_PORT) +"' by best guess."
    
    if not SERIAL_PORT:
        print "-----------------------------------------------------------------------------"
        print "WARNING: TS_BatterySimulator doesn't know what serial device to connect to!"
        print "Make sure the TS_BatterySimulator hardware is connectd to the USB interface."
        if os.name == 'nt':
            print "ON WINDOWS: You will also need to setup the virtual com port."
            print "See 'Installing Drivers': http://arduino.cc/en/Guide/Windows"
        print "-----------------------------------------------------------------------------"      
    
    #start command processor
    commandProcessorThread = threading.Thread(name='commandProcessor',
                         target=CommandProcessor,
                         args=(waitEvent,))
    commandProcessorThread.start()

    
        #start serial processor
    serialProcessorThread = threading.Thread(name='serialProcessor',
                         target=serialProcessor)
    serialProcessorThread.start()
    
    # run
    if args.debug:
        debug(True)
        if hasattr(sys, "_MEIPASS"):
            print "Data root is: " + sys._MEIPASS             
    else:
        if args.host_on_all_interfaces:
            run_with_callback('', NETWORK_PORT)
        else:
            run_with_callback('127.0.0.1', NETWORK_PORT)    

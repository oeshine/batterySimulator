
import os
import sys
import time
import serial
from serial.tools import list_ports
from collections import deque


class SerialManagerClass:
    
    def __init__(self):
        self.device = None

        self.rx_buffer = ""
        self.tx_buffer = ""        
        self.remoteXON = True

        # TX_CHUNK_SIZE - this is the number of bytes to be 
        # written to the device in one go. It needs to match the device.
        self.TX_CHUNK_SIZE = 64
        self.RX_CHUNK_SIZE = 256
    def list_devices(self, baudrate):
        ports = []
        if os.name == 'posix':
            iterator = sorted(list_ports.grep('tty'))
            print "Found ports:"
            for port, desc, hwid in iterator:
                ports.append(port)
                print "%-20s" % (port,)
                print "    desc: %s" % (desc,)
                print "    hwid: %s" % (hwid,)            
        else:
            # iterator = sorted(list_ports.grep(''))  # does not return USB-style
            # scan for available ports. return a list of tuples (num, name)
            available = []
            for i in range(24):
                try:
                    s = serial.Serial(port=i, baudrate=baudrate)
                    ports.append(s.portstr)                
                    available.append( (i, s.portstr))
                    s.close()
                except serial.SerialException:
                    pass
            print "Found ports:"
            for n,s in available: print "(%d) %s" % (n,s)
        return ports


            
    def match_device(self, search_regex, baudrate):
        if os.name == 'posix':
            matched_ports = list_ports.grep(search_regex)
            if matched_ports:
                for match_tuple in matched_ports:
                    if match_tuple:
                        return match_tuple[0]
            print "No serial port match for anything like: " + search_regex
            return None
        else:
            # windows hack because pyserial does not enumerate USB-style com ports
            print "Trying to find Controller ..."
            for i in range(24):
                try:
                    s = serial.Serial(port=i, baudrate=baudrate, timeout=2.0)
                    #lasaur_hello = s.read(32)
                    #if lasaur_hello.find(self.LASAURGRBL_FIRST_STRING) > -1:
                    #    return s.portstr
                    s.close()
                except serial.SerialException:
                    pass      
            return None      
        

    def connect(self, port, baudrate):
        self.rx_buffer = ""
        self.tx_buffer = ""        
        self.remoteXON = True
        self.job_size = 0
                
        # Create serial device with both read timeout set to 0.
        # This results in the read() being non-blocking
        # Write on the other hand uses a large timeout but should not be blocking
        # much because we ask it only to write TX_CHUNK_SIZE at a time.
        # BUG WARNING: the pyserial write function does not report how
        # many bytes were actually written if this is different from requested.
        # Work around: use a big enough timeout and a small enough chunk size.
        self.device = serial.Serial(port, baudrate, timeout=0, writeTimeout=0.1)


    def close(self):
        if self.device:
            try:
                self.device.flushOutput()
                self.device.flushInput()
                self.device.close()
                self.device = None
            except:
                self.device = None
            return True
        else:
            return False
                    
    def is_connected(self):
        return bool(self.device)
        
    def flush_input(self):
        if self.device:
            self.device.flushInput()

    def flush_output(self):
        if self.device:
            self.device.flushOutput()

    def write(self,chars):
        if self.device:
            try:
                self.device.write(chars)
            except:
                return False
        else:
            return False
        return True
    def read_existing(self):
        if self.device:
            try:
                ### receiving
                chars = self.device.read(self.RX_CHUNK_SIZE)
                chars = self.rx_buffer + chars
                self.rx_buffer = ''
                return chars
            except:
                return ""
    def read_to(self,char,timeout=100):
        if self.device:
            try:
                i = 0
                while i< timeout:
                    ### receiving
                    chars = self.device.read(self.RX_CHUNK_SIZE)
                    if len(chars) > 0:
                        self.rx_buffer = self.rx_buffer + chars
                    if char in self.rx_buffer:
                        tmp = self.rx_buffer.split(char)
                        self.rx_buffer = tmp[0].lstrip(tmp[0] + char)
                        return tmp[0]
                    time.sleep(0.01)
                    i +=1
                #print 'time out'
            except:
                print 'error 1'
                return ""
        return ""
# singelton
SerialManager = SerialManagerClass()

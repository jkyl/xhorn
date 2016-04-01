import serial, sys, time

INIT  = 'F C '    # initialize
RUN   = 'R'       # run command
ACCL  = 'A1M'     # acceleration (1 - 127)
SPEED = 'S1M'     # speed (1 - 6000 steps/sec)
INCR  = 'I1M'     # increment steps
ABS   = 'IA1M'    # set absolute position
POS   = 'X'       #


def gen_command(accl = 1, speed = 2000, incr = None, abst = None):
    '''
    Generates a string that specifies speed, acceleration, and whether
    to move incrementally or absolutely. 
    '''
    if incr == None and abst != None:
        move = ABS+str(abst)
    elif abst == None and incr != None:
        move = INCR+str(incr)
    else:
        print('Not a valid move: must specify incr or abst.\n')
        sys.exit()
    return INIT+ACCL+str(accl)+','+SPEED+str(speed)+','+move+','+RUN


def gen_serial_obj(port = '/dev/ttyUSB0', baudrate = 38400):
    '''
    Creates a serial object with the specified baudrate and /dev location. 
    Sets other parameters according to velmex's specs. 
    '''
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baudrate
    ser.bytesize = serial.EIGHTBITS     # number of bits per bytes
    ser.parity = serial.PARITY_NONE     # set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
    ser.timeout = 0                     # no-block read
    ser.xonxoff = False                 # disable software flow control
    ser.rtscts = False                  # disable hardware (RTS/CTS) flow ctrl
    ser.dsrdtr = False                  # disable hardware (DSR/DTR) flow ctrl
    ser.writeTimeout = 2                # timeout for write
    return ser


def send_command(ser, cmd):
    '''
    Opens the serial port, writes a command, and reads back the response. 
    Will close and open again if the port was left open, otherwise throws
    informative exception. 
    '''
    try:
        try:
            ser.flushInput() 
            ser.flushOutput()
            ser.write(cmd)
            while True:
                time.sleep(.02)
                response = ser.readline()
                if response != '':
                    break
            return response
        except Exception, e1:
            print("Error communicating: " + str(e1))          
    except (KeyboardInterrupt, SystemExit):
        ser.close()
        send_command(ser, "D")
        print('\nStopped')
        sys.exit()
        

class Motor:
    '''
    Class that combines the previous functions for quick use. Takes optional
    /dev directory and baudrate args. 

        - position property returns integer of current position. 

        - baudrate property returns integer of current baudrate.

        - status property returns 'busy', 'ready', or 'jog mode'.

        - set_baudrate() method takes baudrate arg and sends command to change
          the vxm baudrate, then generates a new serial object with the same br.
          Recommended that you then use the save_settings() method so the vxm 
          wont re-initialize to the the old br when you turn it on again. 

        - save_settings() method saves the current settings, returns True if 
          succesful. 

        - home() method takes no args and executes sequence for returning home.
          Returns True if succesful.

        - move() method takes optional accl and speed args, and just one of 
          required abst or incr args. Returns integer of position at the end 
          of movement.

        - send() method takes any command string and returns the raw writeback.

    '''
    def __init__(self, port = '/dev/ttyUSB0', baudrate = 38400):
        self._ser = gen_serial_obj(port, baudrate)
        self._ser.open()
        
    @property
    def position(self):
        return int(self.send("X").replace("X", '')[:-1]) / 100.

    @property
    def baudrate(self):
        return self._ser.baudrate

    @property
    def status(self):
        rv = self.send('V')
        if rv == 'B':
            return 'busy'
        elif rv == 'R':
            return 'ready'
        else:
            return 'jog mode'

    def send(self, cmd):
        return send_command(self._ser, cmd)

    def set_baudrate(self, baudrate):
        if self.send("F C setB{}, R".format(str(baudrate)[:2])) == '^':
            self._ser.baudrate = baudrate
            return True
        else:
            return False

    def save_settings(self):
        return self.send('rsm') == '^'
            
    def home(self):
        return self.send("C S1M600, I1M-0, I1M4000, I1M-0,  IA1M-0, R C"+\
                         "S1M600, I1M-0, I1M4000, I1M-0, IA1M-0, R") == '^'
    
    def move(self, accl = 1, speed = 2000, incr = None, abst = None):
        if incr != None:
            incr *= 100.
        else:
            abst *= 100.
        c = gen_command(accl, speed, incr, abst)
        return self.send(c) == '^'
        
        
    
    

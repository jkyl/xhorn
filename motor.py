import serial, sys, time

INIT  = 'F C '    # initialize
RUN   = 'R'       # run command
ACCL  = 'A1M'     # acceleration (1 - 127)
SPEED = 'S1M'     # speed (1 - 6000 steps/sec)
INCR  = 'I1M'     # increment steps
ABS   = 'IA1M'    # set absolute position
POS   = 'X'       # query position


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
    Writes a command, sleeps for 2 ms, attempts to read, and repeats if no response.
    Failsafe is to send "D" in the event of keyboard interrupt. 
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
        send_command(ser, "D")
        print('\nMotor stopped.')
        raise
        
class Motor:
    '''
    Class that uses the previous functions for homing, moving, and querying. Takes 
    optional /dev directory and baudrate args. 

        - position() method returns float of current position. 

        - status() method returns 'busy', 'ready', or 'jog mode'.

        - set_baudrate() method takes baudrate arg and sends command to change
          the vxm baudrate, then generates a new serial object with the same br.
          Recommended that you then use the save_settings() method so the vxm 
          wont re-initialize to the the old br when you turn it on again. 

        - save_settings() method saves the current settings, returns bool of 
          success. 

        - home() method takes no args and executes sequence for returning home.
          Returns bool of success.

        - incr() method increments the motor by a degree amount (must be a multiple
          of 0.01 degs), and returns bool of success. 

        - abst() method moves the motor to an absolute degree position (must be a 
          multiple of 0.01 degs), and returns bool of success. 

        - send() method takes any command string and returns the raw writeback.

        - baudrate property returns integer of current baudrate.

    '''
    def __init__(self, port = '/dev/ttyUSB0', baudrate = 38400):
        self._ser = gen_serial_obj(port, baudrate)
        self._ser.open()
        
    def position(self):
        return int(self.send("X").replace("X", '')[:-1]) / 100.

    @property
    def baudrate(self):
        return self._ser.baudrate

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
    
    def incr(self, degs, accl = 1, speed = 20):
        degs = round(degs, 2)
        cmd = INIT + ACCL + str(accl)+ ',' + SPEED + str(speed * 100)\
              + ',' + INCR + str(degs * 100) + ',' + RUN
        return self.send(cmd) == '^'
        
    def abst(self, degs, accl = 1, speed = 20):
        degs = round(degs, 2)
        cmd = INIT + ACCL + str(accl)+ ',' + SPEED + str(speed * 100)\
              + ',' + ABS + str(degs * 100) + ',' + RUN
        return self.send(cmd) == '^'

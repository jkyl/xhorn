import serial, sys, time

INIT  = 'F C '    # initialize
RUN   = 'R'       # run command
ACCL  = 'A1M'     # acceleration (1 - 127)
SPEED = 'S1M'     # speed (1 - 6000 steps/sec)
INCR  = 'I1M'     # increment steps
ABS   = 'IA1M'    # set absolute position
POS   = 'X'       # query position

SPD = 1000. #steps per degrees

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
    ser.open()
    return ser

def send_command(ser, cmd, n = 0):
    '''
    Writes a command, sleeps for 20 ms, attempts to read, and repeats if no response.
    Sends "D" to stop motor in the event of keyboard interrupt. If the stop command
    also fails, assumes a bad connection and fails out rather than trying again. 
    '''
    try:
        ser.flushInput() 
        ser.flushOutput()
        ser.write(cmd)
        t0 = time.time()
        while True:
            time.sleep(.02)
            response = ser.readline()
            if response != '':
                return response        
    except (KeyboardInterrupt, SystemExit):
        print('\nCommand aborted')
        if n < 1:
            send_command(ser, "D", n = n + 1)
            print('Motor stopped')
            raise
        raise
        
class Motor:
    def __init__(self, port = '/dev/ttyUSB0', baudrate = 38400):
        '''
        Calls gen_serial_obj() to open the given port and baudrate, 
        and sets acceleration and speed to 1 and 20 deg/s
        '''
        self._ser = gen_serial_obj(port, baudrate)
        self.accl = 1
        self.speed = 0.5
    
    def position(self):
        '''
        Queries the motor and returns a float of its position in degrees (rounded to 
        four decimal places).
        '''
        return round(int(self.send("X").replace("X", '')[:-1]) / SPD, 4)

    def status(self):
        '''
        Returns 'busy', 'ready', or 'jog mode'.
        '''
        rv = self.send('V')
        if rv == 'B':
            return 'busy'
        elif rv == 'R':
            return 'ready'
        else:
            return 'jog mode'

    def send(self, cmd):
        '''
        Calls send_command() and returns writeback. 
        '''
        return send_command(self._ser, cmd)

    def set_baudrate(self, baudrate):
        '''
        Sets the controller's baudrate. Use save_settings() to retain for next time. 
        '''
        if self.send("F C setB{}, R".format(str(baudrate)[:2])) == '^':
            self._ser.baudrate = baudrate
            return True
        else:
            return False

    def save_settings(self):
        '''
        Saves the controller's settings. 
        '''
        return self.send('rsm') == '^'
            
    def home(self):
        '''
        Executes a homing sequence using the magnetic limit switch. 
        '''
        return self.send("F C S1M50, I1M-0, I1M4000, I1M-0, IA1M-0, R C"+\
                         "S1M50, I1M-0, I1M4000, I1M-0, IA1M-0, R") == '^'
        
    def _move(self, degs, incr = None, abst = None, accl = None, speed = None):
        '''
        Formats and sends a string for either absolute or relative stepping. 
        '''
        if incr:
            TYPE = INCR
        elif abst:
            TYPE = ABS
        if accl is None:
            accl = self.accl
        if speed is None:
            speed = self.speed
        cmd = ','.join((INIT + ACCL + '{}', SPEED + '{}', TYPE  + '{}', RUN))\
                 .format(int(accl), int(speed * SPD), int(degs * SPD))
        return self.send(cmd) == '^'
        
    def abst(self, degs, accl = None, speed = None):
        '''
        Moves the motor to an absolute position of <degs>, takes optional speed 
        (degs/s) and accl (1 - 127) args. 
        '''
        return self._move(degs, abst = True, accl = accl, speed = speed)

    def incr(self, degs, accl = None, speed = None):
        '''
        Moves the motor to a relative position of <degs>, takes optional speed 
        (degs/s) and accl (1 - 127) args. 
        '''
        return self._move(degs, incr = True, accl = accl, speed = speed)

    @property
    def baudrate(self):
        '''
        Serial baudrate. 
        '''
        return self._ser.baudrate

    @property
    def accl(self):
        '''
        Default acceleration (1 - 127).
        '''
        return self._accl

    @property
    def speed(self):
        '''
        Default speed (deg/s).
        '''
        return self._speed

# xhorn
Code for communicating between CASPER's ROACH2 + 5 Gs/s ADC, Velmex VXM motor controller + B59 rotary table, and Python 2.7.

**Dependencies:**
 * [adc5g]
 * [fit_cores]
 * [corr]
 * [pyserial]
 * [ntplib]
 * [h5py]
 * [numpy]
 * [scipy]
 * [matplotlib]

All can be installed (as root) with `$ pip install <packagename>` except:
 * [adc5g]: ```
   	    $ pip install git+git://github.com/sma-wideband/adc_tests.git
	    ```
 * [fit_cores]: ```
   	 	$ wget https://raw.githubusercontent.com/sma-wideband/adc_tests/master/fit_cores.py
		$ mv fit_cores.py /LibraryPython/2.7/site-packages
		```
		or anywhere in Python's `sys.path`.

**Files:**
 * `spec.py` - A class that initializes a 2048 channel spectrometer on the ROACH board.
 * `motor.py` - A class capable of stepping and reading back the position of the rotary table.
 * `time_sync.py` - Contains functions that determine the system time's offset from UTC using the nearest NTP server.
 * `in_out.py` - Contains functions that read and write arrays of measured spectra along with their associated metadata to and from hdf5 files on disk.
 * `scan.py` - A routine that combines the above methods to measure and record spectra over a range of elevations. 

# Usage

## `scan.py`
To execute a data run with the default parameters:
```
$ python scan.py go
```
or in an IPython terminal:
```python
In [1]: run scan.py go
```
To execute a data run with non-default parameters, call `go()` directly:
```python
In [1]: run scan.py

Usage: "python scan.py go"

In [2]: go(step = 1, home = 0, bound = 60, samp_rate = 4400, acc_len = 1, n_accs = 20,
           port = '/dev/ttyUSB0', ip = '128.135.52.192') # default args
```

`go()` initializes `Spec`, `Motor`, and `h5py.File` objects in order write `n_accs` accumulations to files in the `output` directory at angles separated by `step` degrees, each one `acc_len` seconds long, from 0 to `bound` degrees away from the `home` position of the motor.

Each time the motor returns to `home`, the script closes the current file and opens a new one. All files are automatically named with the current UTC time, which is calculated at each return to `home` by querying an NTP server for the system time's offset from UTC. File I/O and time syncronization operations are accomplished with functions in `in_out.py` and `time_sync.py`. 

##`Spec`

To create a standalone spectrometer instance, run:

```python
from spec import Spec
s = Spec(samp_rate = 4400, acc_len = 1, ip = '128.135.52.192') # default args
```

The `__init__` block prints its progress:

```
Connecting to "128.135.52.192"
Loading "simple_spec.bof"
Deglitching
Setting sample rate to 4400 MHz
Setting accumulation length to 1s
Setting fft shift
Arming PPS
```

Upon rebooting the board, the offset, gain, and phase registers for each of the four cores on the ADC will be cleared. It is recommended that you run:

```python
s.fit_ogp(10) # frequency of test tone in MHz
```

which prints the best-fit values for OGP as determined by a least-squares fit to a sine function at the provided frequency:

```
# 10.00  zero(mV) amp(%)  dly(ps) (adj by .4, .14, .11)
#avg    -0.1680 125.1196 49038.3687
core A  -0.1939 -0.0382 -29.7747
core B  -0.4248 -0.2018 -73.7172
core C   0.2916 -0.0505 -68.5566
core D  -0.3448  0.2905 172.0485

sinad = 34.37
average of 2 measurements
#avg    -0.1680 125.1196   0.0000
core A  -0.1939 -0.0382 -29.7747
core B  -0.4248 -0.2018 -73.7172
core C   0.2916 -0.0505 -68.5566
core D  -0.3448  0.2905 172.0485
```

You can plot the time series data with each core denoted seperately to verify that the fit was succesful:

```python
plt.ion()
s.plot_time(cores = True)
```

##`Motor`
To create an instance of the `Motor` class, run:
```python
from motor import Motor
m = Motor(port = '/dev/ttyUSB0', baudrate = 38400) # default args
```

You can save settings to the VXM controller with `m.save_settings()` - this is how we can initialize the class to a baudrate of 38400, even though the controller's factory baudrate is 9600.

The `home()` method makes use of the B59 rotary table's magnetic limit switch to acheive 0.01 degrees of angular precision. This method, along with `incr()` and `abst()` returns a boolean value of its success, rather than the raw writeback. If raw writeback is desired, use the `send()` method.

For safety reasons, a `KeyboardInterrupt` or `SystemExit` during `send_command()` will trigger the command `"D"`, which decelerates the motor to a stop.
Acceleration and speed arguments of `abst()` and `incr()` in general should not be changed. 

#Acknowledgements
In addition to the [sma_wideband] code that we import verbatim:
 * The initialization and snapping methods in `Spec` are derived from Jack Hickish's [simple_spec].
 * The OGP fitting methods in ```Spec``` are derived from Rurik Primiani's [rww_tools].


[adc5g]: <https://github.com/sma-wideband/adc_tests/tree/master/adc5g>
[corr]: <https://github.com/ska-sa/corr>
[pyserial]: <https://github.com/pyserial/pyserial>
[ntplib]: <https://github.com/Tipoca/ntplib>
[h5py]: <https://github.com/h5py/h5py>
[numpy]: <https://github.com/numpy/numpy>
[scipy]: <https://github.com/scipy/scipy>
[matplotlib]: <https://github.com/matplotlib/matplotlib>
[fit_cores]: <https://github.com/sma-wideband/adc_tests/blob/master/fit_cores.py>
[simple_spec]: <https://github.com/jack-h/ami_correlator_sw/blob/master/ami/scripts/simple_spec/spec_init.py>
[rww_tools]: <https://github.com/sma-wideband/adc_tests/blob/master/rww_tools.py>
[sma_wideband]: <https://github.com/sma-wideband>
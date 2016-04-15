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

All can be installed (as root) with ```pip install <packagename>``` except:
 * [adc5g] and [fit_cores]: ```pip install git+git://github.com/sma-wideband/adc_tests.git```

**Files:**
 * ```spec.py``` - A class that initializes a 2048 channel spectrometer on the ROACH board.
 * ```motor.py``` - A class capable of stepping and reading back the position of the rotary table.
 * ```time_sync.py``` - Contains functions that determine the system time's offset from UTC using the nearest NTP server.
 * ```in_out.py``` - Contains functions that read and write numpy arrays of the measured spectra along with their associated metadata to and from hdf5 files on disk.
 * ```scan.py``` - A routine that combines the above methods to measure and record spectra over a range of elevations. 

# Usage
##```Spec``` class
To create a spectrometer instance by itself, in IPython run:
```python
In [1]: run spec.py

In [2]: s = Spec(samp_rate = 4400, acc_len = 1, ip = '128.135.52.192')
Connecting to "128.135.52.192"
Loading "simple_spec.bof"
Deglitching
Setting sample rate to 4600 MHz
Setting accumulation length to 1 s
Setting fft shift
Arming PPS
```

## ```scan.py```
To execute a data run with the default parameters:
```sh
$ python scan.py go
```
or in IPython:
```python
In [1]: run scan.py go
```
To execute a data run with non-default parameters, call ```go()``` directly:
```python
In [1]: run scan.py

Usage: "python scan.py go"

In [2]: go(acc_len = 0.1, n_accs = 200, port = '/dev/ttyUSB0')
```

#Acknowledgements
In addition to the [sma_wideband] code that we import verbatim:
 * The initialization and snapping methods in the ```Spec``` class are derived from Jack Hickish's [simple_spec].
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
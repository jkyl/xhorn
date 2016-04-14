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
 * [matplotlib]

All can be installed (as root) with ```pip install <packagename>``` except:
 * [adc5g] and [fit_cores]: ```pip install git+git://github.com/sma-wideband/adc_tests.git```

**Files:**
 * _spec.py_ - A class that initializes a 2048 channel spectrometer on the ROACH board.
 * _motor.py_ - A class capable of stepping and reading back the position of the rotary table.
 * _time_sync.py_ - Contains functions that determine the system time's offset from UTC using the nearest NTP server.
 * _in_out.py_ - Contains functions that read and write numpy arrays of the measured spectra along with their associated metadata to and from hdf5 files on disk.
 * _scan.py_ - A routine that combines the above methods to measure and record integrations over a range of elevations. 

# Usage
To execute a data run with the default parameters:
```sh
$ python scan.py go
```
or in iPython:
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
The ```Spec()``` class is heavily derivitave of Jack Hickish's [simple_spec].


[adc5g]: <https://github.com/sma-wideband/adc_tests/tree/master/adc5g>
[corr]: <https://github.com/ska-sa/corr>
[pyserial]: <https://github.com/pyserial/pyserial>
[ntplib]: <https://github.com/Tipoca/ntplib>
[h5py]: <https://github.com/h5py/h5py>
[numpy]: <https://github.com/numpy/numpy>
[matplotlib]: <https://github.com/matplotlib/matplotlib>
[fit_cores]: <https://github.com/sma-wideband/adc_tests/blob/master/fit_cores.py>
[simple_spec]: <https://github.com/jack-h/ami_correlator_sw/blob/master/ami/scripts/simple_spec/spec_init.py>

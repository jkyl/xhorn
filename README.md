# xhorn
Code for communicating between CASPER's ROACH2 + 5 Gs/s ADC, Velmex VXM motor controller + B59 rotary table, and Python 2.7.

**Dependencies:**
 * [adc5g]
 * [corr]
 * [pyserial]
 * [ntplib]
 * [h5py]
 * [numpy]
 * [matplotlib]

**Files:**
 * _spec.py_ - A class that initializes a 2048 channel spectrometer on the ROACH board.
 * _motor.py_ - A class capable of stepping and reading back the position of the rotary table.
 * _time_sync.py_ - Contains functions that determine the system time's offset from UTC using [ntplib].
 * _in_out.py_ - Contains functions that read and write numpy arrays of the measured spectra along with their associated metadata to and from hdf5 files on disk.
 * _scan.py_ - A routine that combines the above methods to perform integrations over a range of angles on the sky. 

# Usage
To execute a data run with the default parameters and write the results to an arbitrary path:
```sh
$ python scan.py path/fname.h5 go
```
or in iPython:
```python
In [1]: run scan.py "path/fname.h5" go
```
To execute a data run with non-default parameters, call ```go()``` directly:
```python
In [1]: run scan.py

Usage: "python scan.py <path/fname.h5> go"

In [2]: go(acc_len = 0.1, n_accs = 200, fname = "output/example.h5")
```




[adc5g]: <https://github.com/sma-wideband/adc_tests/tree/master/adc5g>
[corr]: <https://github.com/ska-sa/corr>
[pyserial]: <https://github.com/pyserial/pyserial>
[ntplib]: <https://github.com/Tipoca/ntplib>
[h5py]: <https://github.com/h5py/h5py>
[numpy]: <https://github.com/numpy/numpy>
[matplotlib]: <https://github.com/matplotlib/matplotlib>
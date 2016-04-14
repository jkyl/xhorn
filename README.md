# xhorn
Code for communicating between CASPER's ROACH2 + 5 Gs/s ADC, Velmex VXM motor controller + B59 rotary table, and Python 2.7.

Dependencies:
 * [adc5g]
 * [corr]
 * [pyserial]
 * [ntplib]
 * [h5py]
 * [numpy]
 * [matplotlib]

Files:
 * spec.py - A class that initializes a 2048 channel spectrometer on the ROACH board.
 * motor.py - A class capable of stepping and reading back the position of the rotary table.
 * time_sync.py - Contains functions that determine the system time's offset from UTC using [ntplib].
 * in_out.py - Contains functions that read and write numpy arrays of the measured spectra along with their associated metadata to and from hdf5 files on disk.
 * scan.py - A routine that combines the above methods to perform integrations over a range of angles on the sky. 

# Usage
To execute a data run with the default parameters and write the results to an arbitrary path, run:
```sh
$ python scan.py <path/fname.h5> go
```
or in iPython,
```ipython
>>> run scan.py <path/fname.hdf5> go
```




[adc5g]: <https://github.com/sma-wideband/adc_tests/tree/master/adc5g>
[corr]: <https://github.com/ska-sa/corr>
[pyserial]: <https://github.com/pyserial/pyserial>
[ntplib]: <https://github.com/Tipoca/ntplib>
[h5py]: <https://github.com/h5py/h5py>
[numpy]: <https://github.com/numpy/numpy>
[matplotlib]: <https://github.com/matplotlib/matplotlib>
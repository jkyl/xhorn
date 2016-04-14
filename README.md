# xhorn
Code for communicating between CASPER's ROACH2 + 5 Gs/s ADC via TCP/IP, Velmex B59 rotary table + VXM controller via serial, and Python 2.7.

Dependencies:
 * [adc5g]
 * [corr]
 * [pyserial]
 * [ntplib]
 * [h5py]
 * [numpy]
 * [matplotlib]

Files:
 * spec.py - Contains a class that initializes a 2048 channel spectrometer on the ROACH board.
 * motor.py - Contains a class capable of stepping and reading back the position of the rotary table.
 * time_sync.py - Contains functions that determine the system time's offset from UTC according to NTP.org's servers
 * in_out.py - Contains functions that read and write numpy arrays of the spectrum measured on the ROACH along with the associated metadata to and from hdf5 files on disk.
 * scan.py - A routine that combines the above methods to perform a data run. 

[adc5g]: <https://github.com/sma-wideband/adc_tests/tree/master/adc5g>
[corr]: <https://github.com/ska-sa/corr>
[pyserial]: <https://github.com/pyserial/pyserial>
[ntplib]: <https://github.com/Tipoca/ntplib>
[h5py]: <https://github.com/h5py/h5py>
[numpy]: <https://github.com/numpy/numpy>
[matplotlib]: <https://github.com/matplotlib/matplotlib>
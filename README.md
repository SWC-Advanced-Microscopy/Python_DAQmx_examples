# Python_DAQmx_examples

NI's officially supported DAQmx package, [nidaqmx ](https://github.com/ni/nidaqmx-python), was released in 2017 for Windows only. 
`nidaqmx` wraps the DAQmx C API using `ctypes` and is documented [here](https://nidaqmx-python.readthedocs.io/en/latest/index.html). 
This repository provides more detailed examples [than those given by NI](https://github.com/ni/nidaqmx-python/tree/master/nidaqmx_examples) and also shows how to couple dynamic plotting with with data acquistion. 
If you wish to use NI's hardware on Linux you can try [PyDAQmx](https://pythonhosted.org/PyDAQmx/index.html). 


## Installation
Install the API, then you can play with the examples.
```
pip install nidaqmx
```


## Notes on hardware
Features differ by DAQ device.
e.g. max sample rates differ, not all devices have clocked digital lines, etc. 
It is possible some examples will not work on certain devices.
If you are using a USB DAQ, keep in mind that the devices are optimised for data throughput not response latency. 
You don't want to service tasks (e.g. pull data off the board) more than about 5 times a second. 
Consequently you should plan to perform larger operations on a USB DAQ than on a PCI or PCIe-based device. 



## See also
* [A wrapper for PyDAQmx](https://github.com/petebachant/daqmx)
* [Equivalent examples for MATLAB](https://github.com/SWC-Advanced-Microscopy/MATLAB_DAQmx_examples)
* [Python-based laser-scanning microscopy examples](https://github.com/SWC-Advanced-Microscopy/SimplePyScanner)

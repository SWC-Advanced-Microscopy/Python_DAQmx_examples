

'''
  Example showing continuous hardware-timed analog input using nidaqmx-python and pyqtgraph
 
  pinidaqmxegs.ai.hardwareContinuousVoltageWithCallBackPyQtPlot
 
  Purpose
  Shows how to do hardware-timed analog input using NI's nidaqmx-python package.
  More details at https://github.com/ni/nidaqmx-python

  This function acquires continuously from one channel and returns the mean continuously.
 
 
  Demonstrated steps:
     1. Create a task.
     2. Create an Analog Input voltage channel and acquire data from channels 0 and 1.
     3. Define the sample rate for the voltage acquisition. Additionally, define 
        the sample mode to be finite, and set the number of channels to be 
        acquired per channel.
     4. Call the Start function
     5. Pull in a fixed number of datapoints and plot to screen with pyqtgraph
        once these have been acquired.

  
  Rob Campbell - SWC, 2020

'''

def hardwareContinuousVoltageWithCallBackPyQtPlot():
    import nidaqmx
    from nidaqmx.constants import (AcquisitionType)  # https://nidaqmx-python.readthedocs.io/en/latest/constants.html
    import numpy as np
    from pyqtgraph.Qt import QtGui, QtCore
    import pyqtgraph as pg

    # Define variables
    sampleRate = 1E3     # Sample Rate in Hz
    pointsToPlot = 100

    # Set up the window
    app = QtGui.QApplication([])
    win = pg.GraphicsLayoutWidget(show=True)
    pg.setConfigOptions(antialias=True)
    tPlot = win.addPlot(title="Scrolling plot")
    curve0 = tPlot.plot(pen='y')
    tPlot.setRange(yRange=(-1,1))
    curve1 = tPlot.plot(pen='g')

    def pullDataAndPlot(tTask, event_type, num_samples, callback_data):
        # Extract data and update plots
        data = task.read(number_of_samples_per_channel=pointsToPlot)
        curve0.setData(np.array(data[0]))
        curve1.setData(np.array(data[1]))
        return 0


    # * Create a DAQmx task named 'softwareTimedVoltage'
    #   More details at: "help dabs.ni.daqmx.Task"
    #   C equivalent - DAQmxCreateTask 
    #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
    task = nidaqmx.Task('hardwareContinuousVoltageWithCallBackPyQtPlot')

    # * Set up analog input 0 and 1
    #   It's is also valid to use device and channel only: task.ai_channels.add_ai_voltage_chan('Dev1/ai0');
    #   But see defaults: help(task.ai_channels.add_ai_voltage_chan)
    #   C equivalent - DAQmxCreateAIVoltageChan
    #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreateaivoltagechan/
    task.ai_channels.add_ai_voltage_chan('Dev1/ai0:1')


    # * Configure the sampling rate and the number of samples
    #   C equivalent - DAQmxCfgSampClkTiming
    #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
    #   More details at: "help(task.cfg_samp_clk_timing)
    #   https://nidaqmx-python.readthedocs.io/en/latest/constants.html
    task.timing.cfg_samp_clk_timing(sampleRate,samps_per_chan=pointsToPlot*2, sample_mode=AcquisitionType.CONTINUOUS)


    # * Registera a callback funtion to be run every N samples
    task.register_every_n_samples_acquired_into_buffer_event(pointsToPlot,pullDataAndPlot)

    # We configured no triggers, so the acquisition starts as soon as hTask.start is run
    # Start the task and plot the data
    task.start()

    # Start Qt event loop (bring up the plot etc). This blocks and so 
    # the plot is presented on screen until the user closes the window.
    # Then the task stops. 
    print('\nClose window to stop acquisition')
    app.exec_()


    task.stop()
    task.close()


if __name__ == '__main__':
    hardwareContinuousVoltageWithCallBackPyQtPlot()
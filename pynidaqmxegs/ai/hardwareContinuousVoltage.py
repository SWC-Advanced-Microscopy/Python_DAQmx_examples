

'''
  Example showing continuous hardware-timed analog input using nidaqmx-python and matplotlib
 
  pinidaqmxegs.ai.hardwareContinuousVoltage
 
  Purpose
  Shows how to do hardware-timed analog input using NI's nidaqmx-python package.
  More details at https://github.com/ni/nidaqmx-python

  This function acquires continuously from one channel and plots the results to screen 
  as acquisition proceeds. The example uses the card's on-board clock but uses no triggers. 
 
 
  Demonstrated steps:
     1. Create a task.
     2. Create an Analog Input voltage channel.
     3. Define the sample rate for the voltage acquisition. Additionally, define 
        the sample mode to be finite, and set the number of channels to be 
        acquired per channel.
     4. Call the Start function
     5. Pull in a fixed number of datapoints and plot to screen with matplotlib
        once these have been acquired.

  
  Rob Campbell - SWC, 2020
 
'''

def hardwareContinuousVoltage():
    import nidaqmx
    from nidaqmx.constants import (AcquisitionType)  # https://nidaqmx-python.readthedocs.io/en/latest/constants.html
    import numpy as np
    import matplotlib.pyplot as plt

    # Define variables
    sampleRate = 1E3     # Sample Rate in Hz
    pointsToPlot = 150

    plt.ion() # Enable pyplot interactive mode
    tPlot, tAx = plt.subplots()
    tLine, = tAx.plot(np.zeros(pointsToPlot),'-')
    tAx.set_title('incoming data')
    tAx.set_xlabel('time [samples]')
    tAx.set_ylabel('voltage [V]')
    tAx.grid()

    print('Opening task (ctrl-c to stop)')
    # * Create a DAQmx task named 'softwareTimedVoltage'
    #   More details at: "help dabs.ni.daqmx.Task"
    #   C equivalent - DAQmxCreateTask 
    #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
    with nidaqmx.Task('hardwareContinuousVoltage') as task:

        # * Set up analog input 0 on device defined by variable devName
        #   It's is also valid to use device and channel only: task.ai_channels.add_ai_voltage_chan('Dev1/ai0');
        #   But see defaults: help(task.ai_channels.add_ai_voltage_chan)
        #   C equivalent - DAQmxCreateAIVoltageChan
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreateaivoltagechan/
        task.ai_channels.add_ai_voltage_chan('Dev1/ai0')


        # * Configure the sampling rate and the number of samples
        #   C equivalent - DAQmxCfgSampClkTiming
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
        #   More details at: "help(task.cfg_samp_clk_timing)
        #   https://nidaqmx-python.readthedocs.io/en/latest/constants.html
        task.timing.cfg_samp_clk_timing(sampleRate,samps_per_chan=pointsToPlot*2, sample_mode=AcquisitionType.CONTINUOUS)
        # We configured no triggers, so the acquisition starts as soon as hTask.start is run
        # Start the task and plot the data
        task.start()

        numUpdates=1
        while True:
          # We reach this point once all data have been read
          data = task.read(number_of_samples_per_channel=pointsToPlot)
          # Plot data points to screen
          tLine.set_ydata((data)) # Replace y data
          tAx.set_title('update #%d' % numUpdates)
          # Ensure points stay in range
          tAx.relim()
          tAx.autoscale_view()
          tPlot.canvas.draw()
          tPlot.canvas.flush_events()
          numUpdates = numUpdates+1

        task.stop()


if __name__ == '__main__':
     hardwareContinuousVoltage()
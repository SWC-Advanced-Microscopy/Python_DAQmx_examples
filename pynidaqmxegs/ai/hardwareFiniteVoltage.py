

'''
  Example showing hardware-timed analog input of a finite number of samples using nidaqmx-python
 
  pinidaqmxegs.ai.hardwareFiniteVoltage
 
  Purpose
  Shows how to do hardware-timed analog input using NI's nidaqmx-python package.
  More details at https://github.com/ni/nidaqmx-python

  This function acquires a finite number of samples from multiple channels and plots
  the results to screen after the acquisition finishes. The example uses the card's
  on-board clock but uses no triggers. 
 
 
  Demonstrated steps:
     1. Create a task.
     2. Create an Analog Input voltage channel.
     3. Define the sample rate for the voltage acquisition. Additionally, define 
        the sample mode to be finite, and set the number of channels to be 
        acquired per channel.
     4. Call the Start function and wait until acquisition is complete.
     5. Read all data and plot to screen.

 
 
  Rob Campbell - SWC, 2020
'''

def hardwareFiniteVoltage():
    import nidaqmx
    import numpy as np
    import matplotlib.pyplot as plt

    # Define variables
    sampleRate = 5E3     # Sample Rate in Hz
    secsToAcquire = 3    # Number of seconds over which to acquire data
    numberOfSamples = int(secsToAcquire * sampleRate)


    '''
    sampleClockSource = 'OnboardClock'; # The source terminal used for the sample Clock. 

        #% Parameters for the acquisition (device and channels)
        devName = 'Dev1';       # the name of the DAQ device as shown in MAX
        taskName = 'hardAI';    # A string that will provide a label for the task

        minVoltage = -10;       # Channel input range minimum
        maxVoltage = 10;        # Channel input range maximum
    '''

    print('Acquiring %d data points' % numberOfSamples)

    # * Create a DAQmx task named 'softwareTimedVoltage'
    #   More details at: "help dabs.ni.daqmx.Task"
    #   C equivalent - DAQmxCreateTask 
    #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
    with nidaqmx.Task('hardwareFiniteVoltage') as task:

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
        task.timing.cfg_samp_clk_timing(sampleRate,samps_per_chan=numberOfSamples, sample_mode=nidaqmx.constants.AcquisitionType(10178))
        # We configured no triggers, so the acquisition starts as soon as hTask.start is run
        # Start the task and plot the data
        task.start()

        # We reach this point once all data have been read
        data = task.read(number_of_samples_per_channel=numberOfSamples)

        # Plot data points to screen
        plt.plot(data)
        plt.xlabel('time [samples]')
        plt.ylabel('voltage [V]')
        plt.grid()
        plt.show()



if __name__ == '__main__':
    hardwareFiniteVoltage
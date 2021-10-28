'''
 Example showing hardware-timed continuous analog output with two channels without using a callback function

 pynidaqmx.ao.hardwareContinuousVoltageNoCallback_twoChannels

 Purpose
 Demonstrates how to do hardware-timed continuous analog output without a callback function. 
 To achieve this we use sample regeneration. The buffer contents is played out repeatedly:
 once the end of the buffer is reached, the DAQ returns to the beginning and resumes from there. 
 This code plays a continuous sine wave out of an analog output channel using the DAQ's 
 internal (on-board) sample clock. The example uses no triggers.


 Monitoring the output
 If you lack an oscilloscope you may physically connect the analog output to 
 an analog input and monitor this using the NI MAX test panel. You likely will need
 to select RSE: http://www.ni.com/white-paper/3344/en/


 Example session:
 AO = pynidaqmx.ao.hardwareContinuousVoltageCallback()
 AO.dev_name = 'Dev2' #optionally change device name to something other than Dev1
 AO.create_task()

 Wiring suggestion:
 If you have no scope connect AO0 to AI0 and AO1 to AI1. Display AI0:1 in the NI MAX AI test panel


 You can also run from the system command line:
 - cd to path containing the function
 - python hardwareContinuousVoltageNoCallback_twoChannels.py to run the demo

  Rob Campbell - SWC, 2020

 
 Also see:
 ANSI C: DAQmx_ANSI_C_examples/AO/MultVoltUpdates-SWTimed.c
 Restrictions on AO tasks: http://digital.ni.com/public.nsf/allkb/2C45C3DC484FF730862570E7007CCBD4?OpenDocument
'''

import nidaqmx
from nidaqmx.constants import (AcquisitionType,RegenerationMode)
import numpy as np

class hardwareContinuousVoltageNoCallback_twoChannels():

    # Class properties

    # Parameters for the acquisition (device and channels)
    dev_name = 'Dev1'      # The name of the DAQ device as shown in MAX
    task_name = 'hardAO'   # A string that will provide a label for the task

    # Task configuration
    sample_rate = 5000                 # Sample Rate in Hz
    waveform = []             # Will contain a waveform to play out of the analog line
    num_samples_per_channel = [] #The length of the waveform
    
    h_task = [] # DAQmx task handle

    def __init__(self, autoconnect=False):

        if autoconnect:
            self.create_task()


    def create_task(self):

        # Build one cycle of a sine wave and scale to 5V to play through AO0.
        # Through AO1 we will play the cosine wave.
        w0 = np.sin(np.linspace(-np.pi,np.pi, 500))*5
        w1 = np.cos(np.linspace(-np.pi,np.pi, 500))*5
        self.waveform=np.stack((w0,w1))
        self.num_samples_per_channel = len(self.waveform)  # The number of samples to be stored in the buffer per channel
        print('Constructed a waveform of length %d that will played at %d samples per second' % \
              (self.num_samples_per_channel, self.sample_rate))

        # * Create a DAQmx task
        #   C equivalent - DAQmxCreateTask 
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
        self.h_task = nidaqmx.Task(self.task_name)


        # * Set up analog output on channels 0 and 1 on device defined by property self.dev_name
        #   C equivalent - DAQmxCreateAOVoltageChan
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreateaovoltagechan/
        # https://nidaqmx-python.readthedocs.io/en/latest/ao_channel_collection.html
        connect_at = '%s/ao0:1' % self.dev_name
        self.h_task.ao_channels.add_ao_voltage_chan(connect_at)


 
        # * Configure the sampling rate and the number of samples
        #   C equivalent - DAQmxCfgSampClkTiming
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
        #   https://nidaqmx-python.readthedocs.io/en/latest/timing.html
        buffer_length = self.num_samples_per_channel*4
        self.h_task.timing.cfg_samp_clk_timing(rate = self.sample_rate, \
                                               samps_per_chan = buffer_length, \
                                               sample_mode = AcquisitionType.CONTINUOUS)


        # * Allow sample regeneration: i.e. the buffer contents will be play continuously
        # When the read buffer becomes empty, the card will return to the start and re-output the same values. 
        # http://zone.ni.com/reference/en-XX/help/370471AE-01/mxcprop/attr1453/
        # For more on DAQmx write properties: http://zone.ni.com/reference/en-XX/help/370469AG-01/daqmxprop/daqmxwrite/
        # For a discussion on regeneration mode in the context of analog output tasks see:
        # https://forums.ni.com/t5/Multifunction-DAQ/Continuous-write-analog-voltage-NI-cDAQ-9178-with-callbacks/td-p/4036271
        self.h_task.out_stream.regen_mode = RegenerationMode.ALLOW_REGENERATION
        print('Regeneration mode is set to: %s' % str(self.h_task.out_stream.regen_mode))



        # * Write the waveform to the buffer with a 5 second timeout in case it fails
        #   Writes doubles using DAQmxWriteAnalogF64
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxwriteanalogf64/
        self.h_task.write(self.waveform, timeout=2)


        print('\n')


    def start_signal(self):
        if not self._task_created():
            return

        self.h_task.start()


    def stop_signal(self):
        if not self._task_created():
            return

        self.h_task.stop()


    # House-keeping methods follow
    def _task_created(self):
        '''
        Return True if a task has been created
        '''

        if isinstance(self.h_task,nidaqmx.task.Task):
            return True
        else:
            print('No task created: run the create_task method')
            return False



if __name__ == '__main__':
    print('\nRunning demo for hardwareContinuousVoltageNoCallback_twoChannels\n\n')
    AO = hardwareContinuousVoltageNoCallback_twoChannels()
    AO.create_task()
    AO.h_task.start()
    input('press return to stop')
    AO.h_task.close()

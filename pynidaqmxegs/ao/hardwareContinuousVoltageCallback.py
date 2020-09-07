'''
 Example showing hardware-timed continuous analog output using a callback function

 function pynidaqmx.ao.hardwareContinuousVoltageCallback

 Purpose
 Demonstrates how to do hardware-timed continuous analog output using a callback function. 
 This means we will not use sample regeneration. i.e. the buffer contents is play out 
 once only and as it empties it is re-filled using a callback funtion.
 This code plays a continuous sine wave out of an analog output channel using the DAQ's 
 internal (on-board) sample clock. The example uses no triggers. The waveform is regenerated 
 continuously using a callback function.


 Monitoring the output
 If you lack an oscilloscope you may physically connect the analog output to 
 an analog input and monitor this using the NI MAX test panel. You likely will need
 to select RSE: http://www.ni.com/white-paper/3344/en/
 

 Example session:
 AO = pynidaqmx.ao.hardwareContinuousVoltageCallback()
 AO.dev_name = 'Dev2' #optionally change device name to something other than Dev1
 AO.create_task()

 You can also run from the system command line:
 - cd to path containing the function
 - python hardwareContinuousVoltageCallback.py to run the demo

 Rob Campbell - SWC, 2020

 
 Also see:
 ANSI C: DAQmx_ANSI_C_examples/AO/MultVoltUpdates-SWTimed.c
 Restrictions on AO tasks: http://digital.ni.com/public.nsf/allkb/2C45C3DC484FF730862570E7007CCBD4?OpenDocument
'''

import nidaqmx
from nidaqmx.constants import (AcquisitionType,RegenerationMode)
import numpy as np

class hardwareContinuousVoltageCallback():

    # Class properties

    # Parameters for the acquisition (device and channels)
    dev_name = 'Dev1'      # The name of the DAQ device as shown in MAX
    task_name = 'hardAO'   # A string that will provide a label for the task
    physical_channel = 0   # A scalar or an array with the channel numbers

    # Task configuration
    sample_rate = 5000                 # Sample Rate in Hz
    waveform = []             # Will contain a waveform to play out of the analog line
    num_samples_per_channel = [] #The length of the waveform
    
    h_task = [] # DAQmx task handle

    def __init__(self, autoconnect=False):

        if autoconnect:
            self.create_task()


    def top_up_buffer(self, hTask, event_type, num_samples, callback_data):
            '''
            This method is the callback for the analog output task.
            It re-fills the output buffer when it is half empty
            '''
            self.h_task.write(self.waveform, timeout=5)
            return 0


    def create_task(self):

        # Build one cycle of a sine wave and scale to 5V to play through the AO line.
        self.waveform=np.sin(np.linspace(-np.pi,np.pi, 500))*5
        self.num_samples_per_channel = len(self.waveform)  # The number of samples to be stored in the buffer per channel
        print('Constructed a waveform of length %d that will played at %d samples per second' % \
              (self.num_samples_per_channel, self.sample_rate))

        # * Create a DAQmx task
        #   C equivalent - DAQmxCreateTask 
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
        self.h_task = nidaqmx.Task(self.task_name)


        # * Set up analog output 0 on device defined by variable dev_name
        #   C equivalent - DAQmxCreateAOVoltageChan
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreateaovoltagechan/
        # https://nidaqmx-python.readthedocs.io/en/latest/ao_channel_collection.html
        connect_at = '%s/ao%d' % (self.dev_name,self.physical_channel)
        self.h_task.ao_channels.add_ao_voltage_chan(connect_at)


 
        # * Configure the sampling rate and the number of samples
        #   C equivalent - DAQmxCfgSampClkTiming
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
        #   https://nidaqmx-python.readthedocs.io/en/latest/timing.html
        buffer_length = self.num_samples_per_channel*4
        self.h_task.timing.cfg_samp_clk_timing(rate = self.sample_rate, \
                                               samps_per_chan = buffer_length, \
                                               sample_mode = AcquisitionType.CONTINUOUS)


        # * Do not allow sample regeneration: i.e. the buffer contents will be play only once
        # When the read buffer becomes empty, the card will not return to the start and re-output the same values. 
        # http://zone.ni.com/reference/en-XX/help/370471AE-01/mxcprop/attr1453/
        # For more on DAQmx write properties: http://zone.ni.com/reference/en-XX/help/370469AG-01/daqmxprop/daqmxwrite/
        # For a discussion on regeneration mode in the context of analog output tasks see:
        # https://forums.ni.com/t5/Multifunction-DAQ/Continuous-write-analog-voltage-NI-cDAQ-9178-with-callbacks/td-p/4036271
        self.h_task.out_stream.regen_mode = RegenerationMode.DONT_ALLOW_REGENERATION
        print('Regeneration mode is set to: %s' % str(self.h_task.out_stream.regen_mode))


        # * Set the size of the output buffer
        #   C equivalent - DAQmxCfgOutputBuffer
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxcfgoutputbuffer/
        #self.h_task.cfgOutputBuffer(num_samples_per_channel);


        # * Write the waveform to the buffer with a 5 second timeout in case it fails
        #   Writes doubles using DAQmxWriteAnalogF64
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxwriteanalogf64/
        self.h_task.write(self.waveform, timeout=2)


        # * Call a function to top up the buffer when half of the samples
        #   have been played out.
        run_after_t_samples = round(self.num_samples_per_channel*0.50) # Run when half the signal has been played
        self.h_task.register_every_n_samples_transferred_from_buffer_event(run_after_t_samples, self.top_up_buffer)

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
    print('\nRunning demo for hardwareContinuousVoltageCallback\n\n')
    AO = hardwareContinuousVoltageCallback()
    AO.create_task()
    AO.start_signal()
    input('press return to stop')
    AO.stop_signal()
    AO.h_task.close()
'''
 Demonstration of simultaneous analog input and output

 pynidaqmx.mixed.AOandAI_sharedClock.py

 Description:
  This example demonstrates how to continuously run data acquisition (AI) 
  and signal generation (AO) at the same time and have the tasks synchronized 
  with one another. Note that a single DAQmx task can support only one type of channel:
  http://digital.ni.com/public.nsf/allkb/4D2E6ABCF652542186256F04004FDAC3
  So we need to make one task for AI, one for AO, and start them synchronously with an 
  internal trigger.

  In this example the AI and AO share a clock. They both start at the same time and
  acquire data at exactly the same rate. 
 
 
  Wiring instructions:
  connect AI0 to AO0 on the DAQ device you are working on. 
 
  You may run this example by changing to the directory containing the file and
  running: python AOandAI_sharedClock.py

'''

import nidaqmx
from nidaqmx.constants import (AcquisitionType,RegenerationMode)
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

class AOandAI_sharedClock():

    # Class properties

    # Parameters for the acquisition (device and channels)
    dev_name = 'Dev1'      # The name of the DAQ device as shown in MAX
    ao_chan = 0            # Channel number for the analog output
    ai_chan = 0            # Channel number of the analog input

    min_voltage = -10      # Channel input range minimum
    max_voltage = 10       # Channel input range maximum


    # Task configuration
    sample_rate = 5000                 # Sample Rate in Hz
    waveform = []             # Will contain a waveform to play out of the analog line
    wave_amplitude = 1.5      # the sinewave we plot will be +/- this number of Volts
    num_samples_per_channel = [] #The length of the waveform
    
    h_task_ao = [] # DAQmx task handle for analog output
    h_task_ai = [] # DAQmx task handle for analog input

    # Properties associated with plotting
    _points_to_plot = []    # scalar defining how many points to plot at once
    _app = []               # QApplication stored here
    _win = []               # GraphicsLayoutWidget stored here
    _plot = []              # plot object stored here
    _curve = []             # pyqtgraph plot object


    def __init__(self, autoconnect=False):

        if autoconnect:
            self.set_up_tasks()


    def top_up_buffer(self, hTask, event_type, num_samples, callback_data):
            '''
            This method is the callback for the analog output task.
            It re-fills the output buffer when it is half empty
            '''
            self.h_task.write(self.waveform, timeout=5)
            return 0


    def set_up_tasks(self):
        '''
        Creates AI and AO tasks. Builds a waveform that is played out through AO using
        regeneration. Connects AI to a callback function to handling plotting of data.
        '''

        # * Create two separate DAQmx tasks for the AI and AO
        #   C equivalent - DAQmxCreateTask 
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
        self.h_task_ao = nidaqmx.Task('mixedao')
        self.h_task_ai = nidaqmx.Task('mixedai')


        # * Connect to analog input and output voltage channels on the named device
        #   C equivalent - DAQmxCreateAOVoltageChan
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreateaovoltagechan/
        # https://nidaqmx-python.readthedocs.io/en/latest/ao_channel_collection.html
        self.h_task_ao.ao_channels.add_ao_voltage_chan( '%s/ao%d' % (self.dev_name,self.ao_chan) )
        self.h_task_ai.ai_channels.add_ai_voltage_chan( '%s/ai%d' % (self.dev_name,self.ai_chan) )



        '''
        SET UP ANALOG INPUT
        '''

        # * Configure the sampling rate and the number of samples
        #   ALSO: set source of the clock to be AO clock is where this example differs from basicAOandAI.py
        # ===> SET UP THE SHARED CLOCK: Use the AO sample clock for the AI task <===
        # The supplied sample rate for the AI task is a nominal value. It will in fact use the AO sample clock. 
        #   C equivalent - DAQmxCfgSampClkTiming
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
        #   More details at: "help(task.cfg_samp_clk_timing)
        #   https://nidaqmx-python.readthedocs.io/en/latest/constants.html
        self._points_to_plot = round(self.sample_rate*0.1)
        self.h_task_ai.timing.cfg_samp_clk_timing(self.sample_rate, \
                                    source= '/%s/ao/SampleClock' % self.dev_name, \
                                    samps_per_chan=self._points_to_plot, \
                                    sample_mode=AcquisitionType.CONTINUOUS)



        # * Registera a callback funtion to be run every N samples
        self.h_task_ai.register_every_n_samples_acquired_into_buffer_event(self._points_to_plot, self._read_and_plot)


        '''
        SET UP ANALOG OUTPUT
        '''

        # Build one cycle of a sine wave and scale to 5V to play through the AO line.
        self.waveform=np.sin(np.linspace(-np.pi,np.pi, 260))*self.wave_amplitude
        self.num_samples_per_channel = len(self.waveform)  # The number of samples to be stored in the buffer per channel
        print('Constructed a waveform of length %d that will played at %d samples per second' % \
              (self.num_samples_per_channel, self.sample_rate))



        # * Configure the sampling rate and the number of samples
        #   C equivalent - DAQmxCfgSampClkTiming
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
        #   https://nidaqmx-python.readthedocs.io/en/latest/timing.html
        self.h_task_ao.timing.cfg_samp_clk_timing(rate = self.sample_rate, \
                                               sample_mode = AcquisitionType.CONTINUOUS)


        # * Do allow sample regeneration: i.e. the buffer contents will play repeatedly (cyclically).
        # http://zone.ni.com/reference/en-XX/help/370471AE-01/mxcprop/attr1453/
        # For more on DAQmx write properties: http://zone.ni.com/reference/en-XX/help/370469AG-01/daqmxprop/daqmxwrite/
        # For a discussion on regeneration mode in the context of analog output tasks see:
        # https://forums.ni.com/t5/Multifunction-DAQ/Continuous-write-analog-voltage-NI-cDAQ-9178-with-callbacks/td-p/4036271
        self.h_task_ao.out_stream.regen_mode = RegenerationMode.ALLOW_REGENERATION



        # * Set the size of the output buffer
        #   C equivalent - DAQmxCfgOutputBuffer
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxcfgoutputbuffer/
        #self.h_task.cfgOutputBuffer(num_samples_per_channel);


        # * Write the waveform to the buffer with a 5 second timeout in case it fails
        #   Writes doubles using DAQmxWriteAnalogF64
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxwriteanalogf64/
        self.h_task_ao.write(self.waveform, timeout=2)



        '''
        Set up the triggering
        '''
        # The AO task should start as soon as the AI task starts.
        #   More details at: "help dabs.ni.daqmx.Task.cfgDigEdgeStartTrig"
        #   DAQmxCfgDigEdgeStartTrig
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgdigedgestarttrig/
        self.h_task_ao.triggers.start_trigger.cfg_dig_edge_start_trig( '/' + self.dev_name + '/ai/StartTrigger' )

        # Note that now the AO task must be started before the AI task in order for the synchronisation to work


    def setup_plot(self):
        # Set up pyqtgraph plot window
        self._app = QtGui.QApplication([])
        self._win = pg.GraphicsLayoutWidget(show=True)
        pg.setConfigOptions(antialias=True)
        self._plot = self._win.addPlot(title='Simultaneous AO and AI')
        self._plot.setLimits(yMin=-2, yMax=2)
        self._curve = self._plot.plot(pen='g')
        self._plot.setYRange(-self.wave_amplitude-0.1, self.wave_amplitude+0.1, padding=0)


    def _read_and_plot(self,tTask, event_type, num_samples, callback_data):
        # Callback function that extract data and update plots
        data = self.h_task_ai.read(number_of_samples_per_channel=self._points_to_plot)
        self._curve.setData(np.array(data))
        return 0


    def start_acquisition(self):
        if not self._task_created():
            return

        self.h_task_ao.start()
        self.h_task_ai.start() # Starting this task triggers the AO task


    def stop_acquisition(self):
        if not self._task_created():
            return

        self.h_task_ai.stop()
        self.h_task_ao.stop()

    # House-keeping methods follow
    def _task_created(self):
        '''
        Return True if a task has been created
        '''

        if isinstance(self.h_task_ao,nidaqmx.task.Task) or isinstance(self.h_task_ai,nidaqmx.task.Task):
            return True
        else:
            print('No tasks created: run the set_up_tasks method')
            return False


if __name__ == '__main__':
    print('\nRunning demo for AOandAI_sharedClock\n\n')
    MIXED = AOandAI_sharedClock()
    MIXED.set_up_tasks()
    MIXED.setup_plot()
    MIXED.start_acquisition()
    input('press return to stop')
    MIXED.stop_acquisition()
    MIXED.h_task_ai.close()
    MIXED.h_task_ao.close()

'''
    Example showing basic hardware-timed (clocked or "real time") analog output
    
    pinidaqmxegs.ao.HardwareBasic
    
    Purpose
    Generates a class that can be used interactively set the voltage of an AO line.
    If instantiated at the Python command prompt, the user can interact with the object.
    If run at the system command line, a demo begins. 


    Wiring suggestion
    To test this without a scope you can connect AI0 to AO0. Then in MAX go to 
    the Analog Input Test Panel and view AI0. Call the run_demo method or call
    script from system command line.

    Rob Campbell - SWC, 2020
'''

import nidaqmx
import numpy as np


class HardwareBasic():

    # Class properties
    h_ao = [] #
    dev_name = 'Dev1'; # Device name of the DAQ we will connect to


    def __init__(self,autoconnect=False):
        if autoconnect:
            self.create_task()

    def create_task(self):
        '''
        Create DAQmx task and connect an AO line

        C equivalent - DAQmxCreateTask 
        http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
        '''

        connectAt = self.dev_name+'/ao0'
        print('Connecting to AO task on %s' % connectAt)
        self.h_ao = nidaqmx.Task('AO_on_demand')

        # * Connect to an AO channel
        # https://nidaqmx-python.readthedocs.io/en/latest/ao_channel_collection.html
        self.h_ao.ao_channels.add_ao_voltage_chan(connectAt) # Connect to the first channel



    def run_demo(self):
        '''
        Runs all the demo methods
        '''
        if not self._task_created():
            return

        sample_rate = 1000
        seconds_to_acquire = 5
        total_samples = sample_rate*seconds_to_acquire
        # Set the sampling rate to 1 kHz and report this to the screen
        # https://nidaqmx-python.readthedocs.io/en/latest/timing.html
        self.h_ao.timing.cfg_samp_clk_timing(rate=sample_rate, samps_per_chan=total_samples)
        print('Set sampling rate to %d' % self.h_ao.timing.samp_clk_rate)


        # Generate sine wave data
        x = np.arange(total_samples)
        sinFreq = 3 # Number of cycles to play out
        y = np.sin(2 * np.pi * sinFreq * (x/total_samples))

        # Write data then start task
        self.h_ao.write(y, auto_start=True)
        self.h_ao.wait_until_done() #Block until all data played

        self.h_ao.close()




    # House-keeping methods follow
    def _task_created(self):
        '''
        Return True if a task has been created
        '''
        if isinstance(self.h_ao,nidaqmx.task.Task):
            return True
        else:
            print('No task created: run the create_task method')
            return False


if __name__ == '__main__':
    AO = on_demand(autoconnect=True)
    AO.run_demo()

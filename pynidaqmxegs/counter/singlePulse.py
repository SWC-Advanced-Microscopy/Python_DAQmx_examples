'''
 Example showing how to create a single pulse on a digital output channel with a timer

 pynidaqmx.counter.singlePulse

  Purpose
  Shows how to flip a single digital line high for a brief period after a fixed delay
  with a counter using the dabs.ni.daqmx wrapper. 


 You can run the example from the system command line:
 - cd to path containing the function
 - python singlePulse.py to run the demo

 Rob Campbell - SWC, 2020


'''

import nidaqmx
from nidaqmx.types import CtrTime

class singlePulse():

    # Parameters for the acquisition (device and channels)
    dev_name = 'Dev1'    # The name of the DAQ device as shown in MAX
    counter_id=1;         # The ID of the counter to use
    low_time = 0.0025;      # How long the pulse stays low (TODO: I think this is after the pulse ends)
    high_time=0.0025;       # How long the pulse is stay high
    initial_delay=2;      # How long to wait before generating the first pulse (seconds)
    output_line = 'PFI4' # Digital line out of which the signal till come
    h_task = []        # DAQmx task handle

    def __init__(self, autoconnect=False):

        if autoconnect:
            self.create_task()



    def create_task(self):

        # * Create a DAQmx task called 'example_clk_task'
        #   C equivalent - DAQmxCreateTask 
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
        self.h_task = nidaqmx.Task('clk_task');


        # * Set up a channel to generate digital pulses and define the pulse properties (onset, duration, )
        #   C equivalent - DAQmxCreateCOPulseChanTime
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxcreatecopulsechantime/
        connect_at = '%s/ctr%d' % (self.dev_name,self.counter_id)
        self.h_task.co_channels.add_co_pulse_chan_time(connect_at)






        # Set the pulses to come out of the line defined in self._output_line instead of the default
        self.h_task.co_channels.all.co_pulse_term =  '/' + self.dev_name + '/' +self.output_line;



    def start_signal(self):
        if not self._task_created():
            return

        sample = CtrTime(high_time=self.high_time, low_time=self.low_time)
        print('Performing sample write: ')
        print(self.h_task.write(sample))

        #self.h_task.start()
        #self.h_task.waitUntilTaskDone(initial_delay+high_time+low_time+1)


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
    print('\nRunning demo for singlePulse\n\n')
    CO = singlePulse()
    CO.create_task()
    CO.start_signal()
    CO.h_task.close()

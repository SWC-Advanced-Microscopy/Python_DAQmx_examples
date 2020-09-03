
'''
    Example showing software-timed (on demand) digital output
    
    pinidaqmxegs.do.softwareBasic
    
    Purpose
    Generates a class that can be used interactively to switch on and off some
    digital lines if instantiated at the Python command prompt. If run at the 
    system command line, a demo begins. 

    The class creates three tasks and makes DO channels in three different ways 
    to show the available options. It writes digital values one at a time to these 
    lines.


    Wiring suggestion
    To test this without a scope you can connect AI0 to USER1 and AI1 to USER2. 
    Then in MAX go to the Analog Input Test Panel and set the channel name to
    "Dev1/ai0:1". Then wire port0/line0 to USER1 and port0/line1 to USER2. This
    will enable you test demo_DOtaskSingle and demo_DOtaskMulti. 


    Rob Campbell - SWC, 2020
'''

import nidaqmx
import time


class softwareBasic():

    # Class properties
    hDO = [] # List of DAQmx tasks
    devName = 'Dev1'; # Device name of the DAQ we will connect to


    def __init__(self,autoconnect=False):
        if autoconnect:
            self.create_tasks()


    def __del__(self):
        # destructor
        self.close_tasks


    def create_tasks(self):
        '''
        Create three DAQmx tasks which we will use to demonstrate different aspects of 
        digital channel control. Note that task names can not contain underscores.

        C equivalent - DAQmxCreateTask 
        http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
        '''

        self.hDO.append(nidaqmx.Task('DOtaskSingle')) # Will have just one line
        self.hDO.append(nidaqmx.Task('DOtaskMulti'))  # Will have multiple lines
        self.hDO.append(nidaqmx.Task('DOtaskPort'))   # Will have multiple lines

        # * Define digital output channels on these tasks
        #   C equivalent - DAQmxCreateDOChan
        #   http://zone.ni.com/reference/en-XX/help/370471AC-01/daqmxcfunc/daqmxcreatedochan/

        # One: create a single channel
        self.hDO[0].do_channels.add_do_chan(self.devName+'/port0/line0') #Open one digital line
        #gives DIGITAL_OUTPUT: 10153
        # Two: create two different logical channels on one task
        self.hDO[1].do_channels.add_do_chan(self.devName+'/port0/line1') #Open multiple digital lines
        self.hDO[1].do_channels.add_do_chan(self.devName+'/port0/line2') #Open multiple digital lines

        # Three: create a single logical channel with three lines
        self.hDO[2].do_channels.add_do_chan(self.devName+'/port0/line3:5')




    # Demo methods follow
    def demo_DOtaskSingle(self):
        '''
        Demo writing to a single line
        '''
        if not self._tasks_added():
            return

        print('\nStarting demo_DOtaskSingle')
        print('Switching %s high for one second then back down again' % self.hDO[0].do_channels.channel_names[0])
        self.hDO[0].write(True)
        time.sleep(1)
        self.hDO[0].write(False)


    def demo_DOtaskMulti(self):
        '''
        Demo showing how to write to digital lines on two different logical channels
        '''
        if not self._tasks_added():
            return
        print('\nStarting demo_DOtaskMulti')

        # Set all lines on task DOtask_multi high:
        print('Switching %s and %s high' % (self.hDO[1].do_channels.channel_names[0],self.hDO[1].do_channels.channel_names[1]))
        self.hDO[1].write([True,True])
        time.sleep(1)

        # Then switch them low one at a time:
        print('Switching %s low' % self.hDO[1].do_channels.channel_names[0])
        self.hDO[1].write([False,True])
        time.sleep(0.5)
        print('Switching %s low' % self.hDO[1].do_channels.channel_names[1])
        self.hDO[1].write([False,False])


    def demo_DOtaskPort(self):
        '''
        Demo showing how to write data to multiple lines one logical channel
       
        '''
        if not self._tasks_added():
            return
        print('\nStarting demo_DOtaskPort')
        # Set the middle line (P0/L4) high

        self.hDO[2].start() # Or can set auto_start to True:  see do.sw_timed_single_chan.py
        self.hDO[2].write([False,True,False])
        time.sleep(1)
        self.hDO[2].write([False,False,False])
        self.hDO[2].stop()

    def run_demo(self):
        '''
        Runs all the demo methods
        '''

        self.demo_DOtaskSingle()
        self.demo_DOtaskMulti()
        self.demo_DOtaskPort()




    # House-keeping methods follow
    def close_tasks(self):
        '''
        Close all tasks
        '''
        if self._tasks_added():
            [tTask.close() for tTask in self.hDO]


    def _tasks_added(self):
        '''
        Return True if tasks have been added to self.hDO
        '''
        if len(self.hDO) == 0:
            print('No tasks created.\n')
            return False
        else:
            return True



if __name__ == '__main__':
    DO = softwareBasic(autoconnect=True)
    DO.run_demo()
    DO.close_tasks()

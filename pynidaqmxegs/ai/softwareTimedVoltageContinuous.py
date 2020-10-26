
'''
  Example showing software-timed analog input using nidaqmx-python

  pynidaqmxegs.ai.softwareTimedVoltageContinuous
 
  Purpose
  Describes how to do software-timed analog input using using nidaqmx-python
  This is unbuffered or "on demand" acquisition. 
 
 
  Demonstrated steps:
     1. Create a task.
     2. Create an Analog Input voltage channel.
     3. Read individual analog points continuously from a single channel.
     4. Plot points as we go with pyqtgraph using a circular buffer to provide
        a scrolling plot.
 
 
  Rob Campbell - SWC, 2020

'''


def softwareTimedVoltageContinuous():
    import nidaqmx
    import numpy as np
    from pyqtgraph.Qt import QtGui, QtCore
    import pyqtgraph as pg
    from collections import deque
    # Set up window
    app = QtGui.QApplication([])

    # Define variables
    maxSamplesToPlot=100
    data = deque(np.zeros(maxSamplesToPlot),maxlen=maxSamplesToPlot)  # pre-allocate a circular numpy buffer

    # Set up plot
    win = pg.GraphicsLayoutWidget(show=True)
    pg.setConfigOptions(antialias=True)
    tPlot = win.addPlot(title="Scrolling plot")
    curve = tPlot.plot(pen='y')

    # Build a task
    # * Create a DAQmx task named 'softwareTimedVoltage'
    #   More details at: "help dabs.ni.daqmx.Task"
    #   C equivalent - DAQmxCreateTask 
    #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
    task = nidaqmx.Task('softwareTimedVoltage')


    # * Set up analog input 0.
    #   It's is also valid to use device and channel only: task.ai_channels.add_ai_voltage_chan('Dev1/ai0');
    #   But see defaults: help(task.ai_channels.add_ai_voltage_chan)
    #   C equivalent - DAQmxCreateAIVoltageChan
    #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreateaivoltagechan/
    task.ai_channels.add_ai_voltage_chan('Dev1/ai0', min_val=-10, max_val=10)


    # This function will pull in one data point and update the plot
    def getDataAndUpdatePlot():
        data.append(task.read())
        curve.setData(np.array(data)) # extract data as a numpy array and plot


    # Set up a timer to pull in data every 50 ms using software timing
    timer = QtCore.QTimer()
    timer.timeout.connect(getDataAndUpdatePlot)
    timer.start(50)

    print('Acquiring data...')

    ## Start Qt event loop (bring up the plot etc)
    app.exec_()

    print('Closing task')
    task.close()



if __name__ == '__main__':
    softwareTimedVoltageContinuous()

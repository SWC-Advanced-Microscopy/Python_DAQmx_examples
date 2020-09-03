import matplotlib.pyplot as plt

'''
This class creates a dynamically updating matplotlib line plot
'''


class updating_matplotlib_plot():
    #Suppose we know the x range
    min_x = 0
    max_x = 10

    def __init__(self):
        #Set up plot
        plt.ion()
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()
        

    def draw_points(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def __call__(self):
        '''
        Runs when the class instance is called with no input arguments
        '''
        import numpy as np
        import time

        xdata = []
        ydata = []
        for x in np.arange(0,10,0.5):
            xdata.append(x)
            ydata.append(np.exp(-x**2)+10*np.exp(-(x-7)**2))
            self.draw_points(xdata, ydata)
            time.sleep(0.15)
        return xdata, ydata


if __name__ == '__main__':
    up_mat_pl = updating_matplotlib_plot()
    up_mat_pl() # Runs: __call__()
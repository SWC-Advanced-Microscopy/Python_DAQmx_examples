import nidaqmx as ni

def demo():

    sys = ni.system.System.local()

    # Display the version number of the driver
    print('\nNI DAQmx driver version: %s\n' % str(sys.driver_version))


    # List all connected device
    print('Connected devices:')

    n=1
    for device in sys.devices:
        print('%d. %s' % (n,device))
        n+=1


    # Let's examin Dev1 more closely
    t_dev = sys.devices['Dev1']

    # Now we have access to loads of info such as all ther terminals in t_dev.ternminals

    print('\n\nAvailable termninals on this DAQ:')
    print(t_dev.terminals)

    print('\n\nWhat''s available:')
    print(dir(t_dev))



if __name__ == '__main__':
    demo()
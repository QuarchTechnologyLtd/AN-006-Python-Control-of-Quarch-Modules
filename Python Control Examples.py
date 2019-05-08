'''
AN-006 - Application note demonstrating python control of quarch modules
This application note was written to be used in conjunction with QuarchPy python package and Quarch modules.

########### VERSION HISTORY ###########

29/03/2018 - Andy Norrie    - Minor edits for formatting and layout
21/03/2018 - Pedro Cruz     - Re-written against quarchpy 1.0
19/09/2017 - Tom Pope       - Moved to QuarchPy library
24/04/2018 - Andy Norrie    - Updated from functional to object form

########### INSTRUCTIONS ###########

1- Connect a Quarch module to your PC via USB, Serial or LAN
2- Comment in one of the 'module = ' lines below, based on the USB/Serial/LAN option you are using
3- Alter the 'module = ' line to specify the correct port/module/IP
4- Select the tests you would like to run from the prompt in the command line

####################################
'''

# '.device' provides connection and control of modules
from quarchpy.device import *


# Import other libraries used in the examples
import time
import sys



''' 
Simple example code, showing connection and control of almost any module
'''
def main():
    #Scan for quarch devices on the system
    deviceList = scanDevices ('all')
    
    # You can work with the deviceList dictionary yourself, or use the inbuilt 'selector' functions to help
    # Here we use the user selection function to display the list and return the module connection string
    # for the selected device
    moduleStr = userSelectDevice (deviceList)

    # Create a device using the module connection string
    myDevice = quarchDevice(moduleStr)
    #myArray = quarchArray(myDevice)

    '''
    Several test functions are available, depending on the module you have chosen to work with
    QuarchSimpleIdentify will work with any module.  Comment others in/out as needed
    '''

    displayTests()
    selectTests(myDevice)

    # Close the module before exiting the script
    myDevice.closeConnection()


def selectTests(myDevice):
    if sys.version_info.major >= 3:
        testSelectStr = input("Enter the tests you would like to run separated by a space for example, 1 3 4 5:")
    else:
        testSelectStr = raw_input("Enter the tests you would like to run separated by a space for example 1 3 4 5:")
    try:
        testSelectList = [int(i) for i in (testSelectStr.split())]
    except:
        raise ValueError("User did not enter a valid integer")
    for i in testSelectList:
        if i == 1:
            QuarchSimpleIdentify(myDevice)  # 1
        if i == 2:
            QuarchArrayExample(myDevice)  # 2 Example for use with an Array Controller
        if i == 3:
            QuarchHotPlugExample(myDevice)  # 3 Example for use with a hot-plug/breaker module
        if i == 4:
            QuarchSwitchExample(myDevice)  # 4 Example for a physical layer switch
        if i == 5:
            QuarchPowerMarginingExample(myDevice)  # 5 Example for a PPM

'''
Simple function to display the lists of tests that are available in this script.
'''
def displayTests():
    print("Located Tests")
    #TODO currently hard coded but could be changed in future.
    print("1)\tQuarchSimpleIdentify\n2)\tQuarchArrayExample\n3)\tQuarchHotPlugExample\n4)\tQuarchSwitchExample\n5)\tQuarchPowerMarginingExample\n")


'''
This function demonstrates a very simple module identify, that will work with any Quarch device
'''
def QuarchSimpleIdentify(device1):
    # Print the module name
    print("Running the simple identify example.\n")
    print("Module Name:"),
    print(device1.sendCommand("hello?"))
   
    # Print the module identify and version information
    print("\nModule Identity Information:\n")
    print(device1.sendCommand("*idn?"))

''' 
This function demonstrates simple control over modules that are attached via an Array Controller.  This will require you to connect to
a QTL1461 or QTL1079 Array Controller, with a module attached on port 1
'''
def QuarchArrayExample(device1):

    '''
    First we will use simple commands to the controller.  This requires us to append the device number of the module
    we want to speak with on the end of every command
    '''
    # Print the controller name
    print("Running the array identify test.")
    print("")
    print("Controller Name:")
    print(device1.sendCommand("hello?"))
    print("")

    # Try to talk to the module on port 1
    print("Communicate with module on port 1")
    devStatus = device1.sendCommand("*idn? <1>")
    if "FAIL" in devStatus:
        print("Error: No module on port <1>")
    else:
        print("Module Name on port 1:")
        print(device1.sendCommand("hello? <1>"))
        print("Check power state of module on array port 1:")
        print(device1.sendCommand("RUN:POWER? <1>"))
    print("")

    '''
    Now we will use the quarchArray and subDevice classes, which allow us to
    handle devices on the controller as if they were directly connected. 
    This is useful as it means the same script can be used with any module, 
    regardless of how it is attached
    '''
    print("Communicate with module on port 1, via array API")
    # First we create a quarchArray from the basic quarchDevice
    myArray = quarchArray(device1)
    # Get the subDevice on port <1> of the array
    myModule1 = myArray.getSubDevice(1)
    # Now run the same commands, but no address list is required

    # Try to talk to the module on port 1
    devStatus = myModule1.sendCommand("*idn?")
    if "FAIL" in devStatus:
        print("Error: No module on port <1>")
    else:
        print("Module Name on port 1:")
        print (myModule1.sendCommand("hello?"))
        print("Check power state of module on array port 1:")
        print(myModule1.sendCommand("RUN:POWER?"))


''' 
This function is a simple demonstration of working with a standard hot-plug module (Drive Modules, Card Modules and Cable Modules will all work with this function)
It will first query the name of the module attached, then move it into a known (plugged) state.  Finally it performs a looped power cycle
'''
def QuarchHotPlugExample(device1):
    # Prints out the ID of the attached module
    print("Running the hot-plug module example.\n")

    print("Module Name:"),
    print(device1.sendCommand("hello?"))

    # Check the power up state of the module
    print("\nChecking the State of the Device and Power up if necessary.")
    isPulled = device1.sendCommand("run:power?")
    print("State of the Device:"),
    print(isPulled + "\n")

    # Ensure the module is in Power up state
    if isPulled == "PULLED":
        print("Device is PULLED. Plugging the device...")
        device1.sendCommand("run:power up")
        for i in xrange(30):
            time.sleep(1)
            print ('Waiting {0}/30 seconds for power up to complete.\r'.format(i)),
        print ("\n")

    #Creating a loop for Hot-Plug cycle
    print("Starting HotPlug cycle:")
    for i in range (1,6):
        print("\n   HotPlug Cycle: %d"%i)
        print("   Pulling the device" + ","),
        # Power down (pull) the device
        device1.sendCommand("run:power down"),
        time.sleep(3)
        
        '''
        Here you could insert your own code to query the host and make sure everything worked and the drive disconnected cleanly
        '''
        
        # Power up (plug) the device
        print("plugging the device.\n"),
        device1.sendCommand("run:power up"),
        time.sleep(3)
        
        '''
        Here you could insert your own code to query the host and make sure everything worked and the drive was enumerated
        '''

    print("\nCycle finished!")

'''
This function is a simple demonstration of working with a switch module.  It is designed to work with SAS switches.
It first displays the name of the attached module, then cycles between 2 different connections, first with the currently selected connection time,
then with a time of 2x the initial value.  The connection time is the delay between the first connection being removed, and the now one being created.
'''
def QuarchSwitchExample(device1):
    print("Running the physical layer switch example.\n")

    # Prints out the ID of the attached module
    print("Controller name:"),
    print(device1.sendCommand("hello?") + "\n")
    
    time.sleep(0.1) # Makes sure the last command had time to be executed.
    # Checks the current delay
    switchDelay = device1.sendCommand("CONFig:MUX Delay?")
    switchDelay = float(switchDelay)
    print("Current current delay is: " + str(switchDelay) + " seconds." +"\n")
    
    # Adds a delay if none. 
    if switchDelay == 0:
        switchDelay = 1
        print ("Set New Delay: ")
        print (device1.sendCommand("CONFig:MUX:DELAY " + str(switchDelay)))

    # Create a new delay, as double the current one, this will be used for the second part of the test.
    newDelay = switchDelay * 2 
    
    # Set a device1 between Port 1 and 8.
    print("   Setting a device1 between Port 1 and Port 8:"),
    print(device1.sendCommand("MUX:CONnect 1 8"))
    # Sleep until the connection is in place
    time.sleep(switchDelay)

    #TODO: Here you would check if your connected equipment is working correctly.

    #Set a device1 between Port 1 and 4.
    print("   Setting a device1 between Port 1 and Port 4:"),
    print(device1.sendCommand("MUX:CONnect 1 4"))
    time.sleep(switchDelay)

    '''
    Here you would check if your connected equipment is working correctly.
    '''

    #Set a delay of double the existing delay.
    print("")
    print("Running the test with new delay:"),
    command = "CONFig:MUX:DELay " + str(int(newDelay))
    print(device1.sendCommand( command))
    print("")
    
    time.sleep(0.1) # Makes sure the last command had time to be executed.
    #Set a device1 between Port 1 and 8
    print("   Setting a device1 between Port 1 and Port 8:"),
    print(device1.sendCommand("MUX:CONnect 1 8"))
    time.sleep(newDelay)

    '''
    Here you would check if your connected equipment is working correctly
    '''

    #Set a device1 between Port 1 and 4
    print("   Setting a device1 between Port 1 and Port 4:"),
    print(device1.sendCommand("MUX:CONnect 1 4"))
    time.sleep(newDelay)

    '''
    Here you would check if your connected equipment is working correctly
    '''

    #Set the switch back to initial delay we had at the start
    print("")
    print("Changing the delay back to the previous settings:"),
    command = "CONFig:MUX:DELay " + str(int(switchDelay))
    print(device1.sendCommand( command))

    print("\nTest concluded!")

'''
This function works with our Programmable Power Modules, and demonstrates how to identify the module, set the power output then perform a series
of simple power margining measurements
'''
def QuarchPowerMarginingExample(device1):
    print("Running the power module example.\n")

    # Prints out the ID of the attached module.
    print("Module attached:"),
    print(device1.sendCommand("hello?") + "\n")

    #Set the 5V channel and 12V channel to 5000mV and 12000mV to ensure that they are at the right level.
    print ("Setting PPM into default voltage state.\n")
    device1.sendCommand("Sig:5v:Volt 5000")
    device1.sendCommand("Sig:12v:Volt 12000")
    device1.sendCommand("CONF:OUT:MODE 5v")

    #Check the state of the module and power up if necessary.
    print("Checking the State of the Device and power up if necessary.")
    currentState = device1.sendCommand("run:power?")
    print("State of the Device: " + (currentState))
    
    # If the outputs are off
    if currentState =="OFF":
        # Power up
        device1.sendCommand("run:power up"),
        print("Powering up the device:"),
        # Let the attached device power up fully
        time.sleep(3)
        print ("OK!")

    # Print headers
    print("\nRunning power margining test...\n")
    print("Margining Results for 12V rail:\n")

    # Loop through 6 different voltage levels, reducing by 200mV on each loop
    testVoltage = 12000
    i = 0
    for i in range (6):

        # Set the new voltage level
        device1.sendCommand("Sig:12V:Volt " + str(testVoltage))

        # Wait for the voltage rails to settle at the new level
        time.sleep(1)

        # Request and print(the voltage and current measurements
        print(device1.sendCommand("Measure:Voltage 12V?")+  " = "  + device1.sendCommand("Measure:Current 12V?"))

        # Decreasing the testVoltage by 200mv
        testVoltage -= 200

    # Set the 12v level aback to default
    print("\nSetting the 12V back to default state.\n")
    device1.sendCommand("Sig:12V:Volt 12000")

    # Print headers
    print("Margining Results for 5V rail:\n")

    # Loop through 6 different voltage levels, reducing by 200mV on each loop
    testVoltage = 5000
    i = 0
    for i in range (6):

        # Set the new voltage level
        device1.sendCommand("Sig:5V:Volt " + str(testVoltage))
        # Wait for the voltage rails to settle at the new level
        time.sleep(1)
        # Request and print(the voltage and current measurements
        print(   device1.sendCommand("Measure:Voltage 5V?")+  " = "  + device1.sendCommand("Measure:Current 5V?"))
        # Decreasing the testVoltage by 200mv
        testVoltage -= 200

    print("\nSetting the 5V back to default state.\n")
    device1.sendCommand("Sig:5V:Volt 5000")

    print("Test finished!")


if __name__== "__main__":
 main()

'''
AN-006 - Application note demonstrating python control of quarch modules
This application note was written to be used in conjunction with QuarchPy python package and Quarch modules.

########### VERSION HISTORY ###########

19/09/2017 - Tom Pope       - Moved to QuarchPy library
21/03/2018 - Pedro Cruz     - Re-written against quarchpy 1.0
29/03/2018 - Andy Norrie    - Minor edits for formatting and layout
24/04/2018 - Andy Norrie    - Updated from functional to object form
12/05/2021 - Matt Holsey    - Fixed power margining bug - 3v3 vs 5v rail

########### INSTRUCTIONS ###########

1- Connect a Quarch module to your PC via USB, Serial or LAN
2- Either select the module in the module selection dialogue or comment in the 'module = ' line below, based on the USB/Serial/LAN option you are using
3- Select the tests you would like to run from the prompt in the command line

####################################
'''

# Import other libraries used in the examples
import time

# '.device' provides connection and control of modules
from quarchpy.device import *
from quarchpy.user_interface import user_interface

''' 
Simple example code, showing connection and control of almost any module
'''
def main():
    #Main Loop
    while True:

        #Scan for quarch devices over all connection types
        deviceList = scanDevices('all', favouriteOnly=False)

        # You can work with the deviceList dictionary yourself, or use the inbuilt 'selector' functions to help
        # Here we use the user selection function to display the list and return the module connection string
        # for the selected device
        moduleStr = userSelectDevice(deviceList,additionalOptions = ["Rescan","All Conn Types","Quit"], nice=True)
        if moduleStr == "quit":
            return 0

        #If you know the name of the module you would like to talk to then you can skip module selection and hardcode the string.
        #moduleStr = "USB:QTL1999-05-005"

        # Create a device using the module connection string
        myDevice = getQuarchDevice(moduleStr)

        #Check if the module selected is attached to an array controller a QTL1461 or QTL1079
        if moduleStr.__contains__("<") and moduleStr.__contains__(">"):
            portNumber = int(moduleStr[moduleStr.find("<") + 1: moduleStr.find(">")])
            myDevice = quarchArray(myDevice).getSubDevice(portNumber)


        #Several test functions are available, depending on the module you have chosen to work with
        #QuarchSimpleIdentify will work with any module.
        selectTests(myDevice)

        # Close the module before exiting the script
        myDevice.closeConnection()

def selectTests(myDevice):
    #Create a list of test that can be selected
    listOfTests = ["QuarchSimpleIdentify", "QuarchArrayExample", "QuarchHotPlugExample", "QuarchSwitchExample", "QuarchPowerMarginingExample", "PowerTest"]
    #Pass the list to QuarchPy's listSelection function.
    testSelectList = user_interface.listSelection(message="Enter the number for the test you would like to run",selectionList=listOfTests, nice = True, tableHeaders=["Test Name"], indexReq=True, align="l")

    #Identify what test has been selected and run it
    if testSelectList == "QuarchSimpleIdentify":
        QuarchSimpleIdentify(myDevice)  # 1
    elif testSelectList == "QuarchArrayExample":
        QuarchArrayExample(myDevice)  # 2 Example for use with an Array Controller
    elif testSelectList == "QuarchHotPlugExample":
        QuarchHotPlugExample(myDevice)  # 3 Example for use with a hot-plug/breaker module
    elif testSelectList == "QuarchSwitchExample":
        QuarchSwitchExample(myDevice)  # 4 Example for a physical layer switch
    elif testSelectList == "QuarchPowerMarginingExample":
        QuarchPowerMarginingExample(myDevice)  # 5 Example for a PPM
    elif testSelectList == "PowerTest":
        PowerTest(myDevice)  # 5 Example for any power module PAM or PPM


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
This function demonstrates simple control over modules that are attached via an Array Controller. This will require you to connect to
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
        i=0
        while i<30:
            time.sleep(1)
            print ('Waiting {0}/30 seconds for power up to complete.\r'.format(i)),
            i+=1
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

    # Checking output mode of device
    print("Module output mode:")
    out_mode = device1.sendCommand("conf:out:mode?")
    print(str(out_mode))

    testVoltage2 = 5000
    if "3v3" in str(out_mode).lower():
        testVoltage2 = 3300

    #Set the 5V channel and 12V channel to 5000mV and 12000mV to ensure that they are at the right level.
    print ("Setting PPM into default voltage state.\n")
    device1.sendCommand("Sig:{0}:Volt {1}".format(out_mode, str(testVoltage2)))
    device1.sendCommand("Sig:12v:Volt 12000")

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
    print("Margining Results for {0} rail:\n".format(out_mode))

    # Loop through 6 different voltage levels, reducing by 200mV on each loop
    i = 0
    for i in range (6):

        # Set the new voltage level
        device1.sendCommand("Sig:{0}:Volt {1}".format(out_mode, str(testVoltage2)))
        # Wait for the voltage rails to settle at the new level
        time.sleep(1)
        # Request and print(the voltage and current measurements
        print(device1.sendCommand("Measure:Voltage {0}?".format(out_mode)) +
              " = "  + device1.sendCommand("Measure:Current " + out_mode + "?"))

        # Decreasing the testVoltage by 200mv
        testVoltage2 -= 200

    # Resetting rail back to original state.
    print("\nSetting the {0} back to default state.\n".format(out_mode))
    device1.sendCommand("Sig:{0}:Volt {1}".format(out_mode, "3300" if out_mode == "3v3" else "5000" ))

    print("Test finished!")

def PowerTest(device1):
    print("Running the PAM Test example.\n")

    # Prints out the ID of the attached module.
    print("Module attached:"),
    print(device1.sendCommand("hello?") + "\n")

    # Check the state of the module and power up if necessary.
    print("Checking the State of the Device and power up if necessary.")
    currentState = device1.sendCommand("run:power?")
    print("State of the Device: " + (currentState))

    # If the outputs are off
    if currentState.lower() == "pulled" or currentState.lower() == "off":
        # Power up
        print("Powering up the device:")
        retVal = device1.sendCommand("run:power up")
        if "CONF:OUT:MODE " in retVal:
            # Set the 5V channel and 12V channel to 5000mV and 12000mV to ensure that they are at the right level.
            print("Setting PPM into default voltage state.\n")
            device1.sendCommand("Sig:5v:Volt 5000")
            device1.sendCommand("Sig:12v:Volt 12000")
            device1.sendCommand("CONF:OUT:MODE 5v")
            retVal = device1.sendCommand("run:power up")
        print(retVal)

        # Let the attached device power up fully
        time.sleep(3)

    #Display all power data + digital signals for the fixture attached
    print(device1.sendCommand("measure:outputs?"))

    print("Test finished!")
if __name__== "__main__":
    main()

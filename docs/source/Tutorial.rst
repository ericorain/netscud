Tutorial
####################

This tutorial is made of examples to learn gradually how to use asynchronous SSH programming for network device (i.e. network switches or routers) with netscud.

Simple command
**************

This first example is a very basic program that sends a command to a device then print it out.

Here is the complete example:

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      my_device = {
         "ip": "192.168.0.16",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_ios",
      }

      # Creation of a device
      async with netscud.ConnectDevice(**my_device) as sw1:

         # Command to send
         cmd = "show interfaces description"

         # Sending command
         output = await sw1.send_command(cmd)

         # Display message
         print(output)


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())

**Explanation:**

At the beginning it shows how to define the parameters of a network device (IP address, Login, Password and Device type) with a python dictionary. Parameters must be adapted according to your device.

.. code-block:: Python

   my_device = {
      "ip": "192.168.0.16",
      "username": "cisco",
      "password": "cisco",
      "device_type": "cisco_ios",
   }

netscud.ConnectDevice() is a function that is used for connecting a device and returns an object used to interact with the device with various methods. The default connection is performed in SSH. Do pay attention that a "with" instruction is used (also known as context manager) which allows to have an automatic close of the connection with the device.

.. code-block:: Python

   # Creation of a device
   async with netscud.ConnectDevice(**my_device) as sw1:

Commands to the device is sent with send_command() method. Parameters to send_commands can be a string variable (send_command(cmd)) or a string (send_command("show interfaces description")). A string with the result of the command is returned; here in the output variable. send_command() is used for sending reading commands to a device; it is not made for writing commands to a device (like send_config_set() below).

.. code-block:: Python

   # Sending command
   output = await sw1.send_command(cmd)


Then the result is printed out on the screen.

.. code-block:: Python

   # Display message
   print(output)

On a Cisco IOS device the "show interfaces description" should look like this:

.. code-block::

   R1#show interfaces description
   Interface                      Status         Protocol Description
   Fa0/0                          up             up
   Fa0/1                          up             up
   Fa1/0                          up             up
   Fa1/1                          up             up
   Et2/0                          up             up
   Et2/1                          up             up
   Et2/2                          up             up
   Et2/3                          up             up
   R1#

The first example script would give that result:

.. code-block::

   c:\>simple_command.py
   Interface                      Status         Protocol Description
   Fa0/0                          up             up
   Fa0/1                          up             up
   Fa1/0                          up             up
   Fa1/1                          up             up
   Et2/0                          up             up
   Et2/1                          up             up
   Et2/2                          up             up
   Et2/3                          up             up

   c:\>

Without context manager
***********************

netscud allows not to use context manager ("with" instruction) but in that case more commands are needed for the same purpose. Example 1 is preferred since there is no need to close connections manually which is less prone to errors.

Here is an example:

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      my_device = {
         "ip": "192.168.0.16",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_ios",
      }

      # Creation of a device
      sw1 = netscud.ConnectDevice(**my_device)

      # Connection to the device
      await sw1.connect()

      # Command to send
      cmd = "show interfaces description"

      # Sending command
      output = await sw1.send_command(cmd)

      # Display message
      print(output)

      # Disconnection
      await sw1.disconnect()


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())


Config command
**************

send_command() sends commands mostly for reading information (like Cisco IOS "show" commands). But in order to send configuration commands to a switch or a router send_config_set() is to be used. Basically send_config_set() is equivalent as all the commands that can be sent in "configure terminal" mode on Cisco IOS devices.

In this example 3 commands are sent to a network device:

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      my_device = {
         "ip": "192.168.0.16",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_ios",
      }

      # Connection to the device
      async with netscud.ConnectDevice(**my_device) as sw1:

         # Commands to send
         cmds = [
               "interface FastEthernet1/0",
               "ip address 1.1.1.1 255.255.255.0",
               "no shutdown",
         ]

         # Sending command
         output = await sw1.send_config_set(cmds)

         # Display message
         print(output)


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())

**Explanation:**

send_config_set() accepts either a string or a list of strings; in this case all the strings are commands to configure the network device.

In this example a list of 3 commands are selecting an interface, set its IP address then enable it.

.. code-block:: Python

   # Commands to send
   cmds = [
         "interface FastEthernet1/0",
         "ip address 1.1.1.1 255.255.255.0",
         "no shutdown",
   ]

   # Sending command
   output = await sw1.send_config_set(cmds)


Thus before this program a network device could get this configuration:

.. code-block::

   R1#show ip interface brief
   Interface              IP-Address      OK? Method Status                Protocol
   FastEthernet0/0        192.168.0.16    YES NVRAM  up                    up
   FastEthernet0/1        unassigned      YES manual up                    up
   FastEthernet1/0        unassigned      YES manual administratively down down
   FastEthernet1/1        unassigned      YES DHCP   up                    up
   Ethernet2/0            unassigned      YES DHCP   up                    up
   Ethernet2/1            unassigned      YES NVRAM  up                    up
   Ethernet2/2            unassigned      YES NVRAM  up                    up
   Ethernet2/3            unassigned      YES NVRAM  up                    up
   R1#

At runtime the program gives that result:

::

   c:\>config_command.py
   configure terminal
   Enter configuration commands, one per line.  End with CNTL/Z.
   R1(config)#interface FastEthernet1/0
   R1(config-if)#ip address 1.1.1.1 255.255.255.0
   R1(config-if)#no shutdown
   R1(config-if)#exit
   R1(config)#

   c:\>


Then on the network device we have that configuration:

.. code-block::

   R1#show ip interface brief
   Interface              IP-Address      OK? Method Status                Protocol
   FastEthernet0/0        192.168.0.16    YES NVRAM  up                    up
   FastEthernet0/1        unassigned      YES manual up                    up
   FastEthernet1/0        1.1.1.1         YES manual up                    up
   FastEthernet1/1        unassigned      YES DHCP   up                    up
   Ethernet2/0            unassigned      YES DHCP   up                    up
   Ethernet2/1            unassigned      YES NVRAM  up                    up
   Ethernet2/2            unassigned      YES NVRAM  up                    up
   Ethernet2/3            unassigned      YES NVRAM  up                    up
   R1#


Managing exceptions
*******************

It can be useful to manage an error triggered by an exception. The following example shows how to do that.

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      my_device = {
         "ip": "192.168.0.16",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_ios",
      }

      try:

         # Connection to the device
         async with netscud.ConnectDevice(**my_device) as sw1:

               # Command to send
               cmd = "show interfaces subscription"

               try:

                  # Sending command
                  output = await sw1.send_command(cmd)

                  # Display message
                  print(output)

               except Exception as error:

                  # Error during connection

                  # Display message
                  print("Error:\n" + str(error))

                  # Leave the program
                  return

      except Exception as error:

         # Error during connection

         # Display message
         print("Error: " + str(error))

         # Leave the program
         return


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())


**Explanation:**

The command sent is wrong for a Cisco IOS device: "show interfaces subscription" command which does not exist is sent to the device instead of "show interfaces description".

The result would be the following if we do not catch the exceptions:

::

   c:\>managing_exceptions.py
   Traceback (most recent call last):

   [...]

      raise Exception(output)
   Exception:                      ^
   % Invalid input detected at '^' marker.
   Exception ignored in: <function _ProactorBasePipeTransport.__del__ at 0x03DF6850>
   Traceback (most recent call last):
   File "C:\Python3\lib\asyncio\proactor_events.py", line 116, in __del__
   File "C:\Python3\lib\asyncio\proactor_events.py", line 108, in close
   File "C:\Python3\lib\asyncio\base_events.py", line 719, in call_soon
   File "C:\Python3\lib\asyncio\base_events.py", line 508, in _check_closed
   RuntimeError: Event loop is closed

   c:\>


The first "try ... except" is used for connection problems. The error message after the "except Exception as error:" part can be adapted to your needs.

.. code-block:: Python
   :emphasize-lines: 1,11-19

   try:

      # Connection to the device
      async with netscud.ConnectDevice(**my_device) as sw1:

            # Command to send
            cmd = "show interfaces subscription"

            [...]

   except Exception as error:

      # Error during connection

      # Display message
      print("Error: " + str(error))

      # Leave the program
      return

The second "try ... except" is used for errors with the command sent. It can be a wrong command or a time out.

.. code-block:: Python
   :emphasize-lines: 4,12-20

   # Command to send
   cmd = "show interfaces subscription"

   try:

      # Sending command
      output = await sw1.send_command(cmd)

      # Display message
      print(output)

   except Exception as error:

      # Error during connection

      # Display message
      print("Error:\n" + str(error))

      # Leave the program
      return

Then the result with the exceptions caught gives:

::

   c:\>managing_exceptions.py
   Error:
                        ^
   % Invalid input detected at '^' marker.

   c:\>

API
***

Some commands are common to many devices that is why some API commands have been added to netscud.

The API commands have two advantages:

* There is not need to remember the network device command
* A single command can used for many different type devices 

The second advantage is very useful in a concurrency program (we will see that in "Inventory advanced" chapter).

That example below show how to use the API get_model() method on a Cisco SG3XX device.

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      my_device = {
         "ip": "192.168.0.2",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_s300",
      }

      # Creation of a device
      async with netscud.ConnectDevice(**my_device) as device:

         # Sending command
         output = await device.get_model()

         # Display message
         print(output)


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())

**Explanation:**


The get_model() method of the network device is giving the model of the current device in the output variable (a string type).

.. code-block:: Python

   # Sending command
   output = await device.get_model()

The result of the script depends on the network device. So here is an example of result for a Cisco SG3XX device:

::

   c:\>api.py
   SG350-10 10-Port Gigabit Managed Switch

   c:\>

.. note::

   The list of all API is available in the API chapter, see :ref:`API_REF`.

Inventory simple
****************

Since it can be annoying to specify all devices in a script netscud provide a way to use inventories. An inventory is a list of devices with their parameters and is stored in a yaml file.

Scripts can be reused with different inventories and the login and password are not stored in the code.

Like the dictionary used in script it defines a device with:

* A Reference (it could be its name)
* IP address
* Login
* Password
* Device type

By default the inventory file is called "hosts.yaml" and is located in "./inventory".

Here is an example of inventory "./inventory/hosts.yaml":

.. code-block:: yaml

   Device1:
      ip: 192.168.0.1
      username: cisco
      password: cisco
      device_type: cisco_s300

   Device2:
      ip: 192.168.0.2
      username: cisco
      password: cisco
      device_type: cisco_ios

So basically 2 devices are defined with their parameters: one for a Cisco SG3XX network device and another one for a Cisco IOS device.

The following example shows how to use the inventory but do not explain how to use it with a device; that will be seen in the next chapter.

.. code-block:: Python

   # Python library import
   import asyncio, netscud

   # from netscud import Inventory
   from netscud.inventory import Inventory


   async def main_task():
      """
      Async main function
      """

      # Create an inventory with the devices from yaml file
      My_inventory = Inventory()

      # Get the list of all devices from the inventory
      my_devices = My_inventory.get_all_devices()

      # Display message
      print("All the devices:")

      # Display the devices one by one
      for device in my_devices:
         print(device)

      # Get the list of some devices from the inventory
      my_devices = My_inventory.select(device_type="cisco_ios")

      # Display message
      print("\nCisco IOS devices:")

      # Display the devices one by one
      for device in my_devices:
         print(device)


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(main_task())

**Explanation:**

The first thing to do is to import the Inventory class. That class will be used to load and manipulate the data into the inventory.

.. code-block:: Python

   # from netscud import Inventory
   from netscud.inventory import Inventory

This instruction creates an Inventory object and read the "./inventory/hosts.yaml" file.

.. code-block:: Python

      # Create an inventory with the devices from yaml file
      My_inventory = Inventory()

Then there are 2 options:

* Either we get the list of all the devices
* Or we filter (i.e. select) only the devices we want

a) All the devices

get_all_devices() method is giving back all the devices of the inventory. The list is a list of dictionaries; it is similar as an inline declaration of devices in a script.

.. code-block:: Python

      # Get the list of all devices from the inventory
      my_devices = My_inventory.get_all_devices()

B) Filtering devices

It is possible to select a device from the Inventory with:

* Its name ("name")
* Its device type ("device_type")

So mainly the filter method will be used for selection a specific device (with its name or IP address) or a group de device of the same type.

The method used for selecting a group of device is called select() and is expecting a parameter with a string value.

The following command from the example select all the devices the "device_type" parameter set to "cisco_ios"; that is all the Cisco IOS devices of the inventory. In this example just one device is selected.

.. code-block:: Python

      # Get the list of some devices from the inventory
      my_devices = My_inventory.select(device_type="cisco_ios")

The result of the script is this one; it first display all the devices then a specific type of device:

::

   c:\>inventory_simple.py
   All the devices:
   {'ip': '192.168.0.1', 'username': 'cisco', 'password': 'cisco', 'device_type': 'cisco_s300', 'name': 'Device1'}
   {'ip': '192.168.0.2', 'username': 'cisco', 'password': 'cisco', 'device_type': 'cisco_ios', 'name': 'Device2'}

   Cisco IOS devices:
   {'ip': '192.168.0.2', 'username': 'cisco', 'password': 'cisco', 'device_type': 'cisco_ios', 'name': 'Device2'}

   c:\>

Inventory advanced
******************

The previous chapter introduced the management of an inventory.

This chapter explains how to use netscud inventories with:

* API commands
* Managing exceptions
* Using concurrency

.. code-block:: Python

   # Python library import
   import asyncio, netscud

   # from netscud import Inventory
   from netscud.inventory import Inventory


   async def run_client(**host):
      """
      async function used by each device individually

      """

      # Default returned value
      output = ""

      try:

         # Connection to the device
         async with netscud.ConnectDevice(**host) as device:

               # Sending command
               output = await device.get_version()

               # Display message
               print("output: '" + str(output) + "'")

      except:

         # If something is wrong then an error message is displayed
         print("Error")

      # Return result
      return output


   async def main_task():
      """
      Async main function
      """

      # Create an inventory with the devices from yaml file
      My_inventory = Inventory()

      # Get the list of all devices from the inventory
      my_devices = My_inventory.get_all_devices()

      # Create a group of tasks (generator) for all the devices
      tasks = (run_client(**device) for device in my_devices)

      # Run the tasks concurrently and collect the results
      result = await asyncio.gather(*tasks)

      # Display message
      print("\nResult:\n'" + str(result) + "'")


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(main_task())

**Explanation:**

The inventory "./inventory/hosts.yaml" is the same as before:

.. code-block:: yaml

   Device1:
      ip: 192.168.0.1
      username: cisco
      password: cisco
      device_type: cisco_s300

   Device2:
      ip: 192.168.0.2
      username: cisco
      password: cisco
      device_type: cisco_ios

After main_task() aync function is launched an inventory is read and all the devices of this inventory is stored into a list of devices in the my_devices variable.

.. code-block:: Python

   # Create an inventory with the devices from yaml file
   My_inventory = Inventory()

   # Get the list of all devices from the inventory
   my_devices = My_inventory.get_all_devices()


Then a generator called "tasks" is created with the list of devices. If you are not familiar with generator concept just copy or adapt the command.

run_client() is the function used for all devices. It takes as parameter a device with all its parameters.

.. code-block:: Python

   # Create a group of tasks (generator) for all the devices
   tasks = (run_client(**device) for device in my_devices)

We have created the "tasks" generator in order to send concurrent commands to the asyncio function gather(). gather() runs functions in concurrency. This example using gather() function shows well one of the advantage of using async techniques in network programming; no needs of processes or threads.

gather() must be awaited and is expecting the generator "tasks" as a parameter. The result is a list of answers for each devices. The gather() function is ended when all tasks are finished.

.. code-block:: Python

   # Run the tasks concurrently and collect the results
   result = await asyncio.gather(*tasks)

run_client() runs an API command for each device to get the version of the device and then print out the result. If an error occurs then an exception is caught and a message ("Error") is displayed.

Finally if a result has been returned by the device then it is returned so that gather will get the value for that specific device. The message disaplyed by print function is not mandatory; it is just here for educational purpose and could be remove.

.. code-block:: Python

   async def run_client(**host):
      """
      async function used by each device individually

      """

      # Default returned value
      output = ""

      try:

         # Connection to the device
         async with netscud.ConnectDevice(**host) as device:

               # Sending command
               output = await device.get_version()

               # Display message
               print("output: '" + str(output) + "'")

      except:

         # If something is wrong then an error message is displayed
         print("Error")

      # Return result
      return output

The result of the script is the following. As you can see every time the run_client() function is run a "print("output") is displayed but as said before it could be remove. The result received by gather() in the result variable is a list of strings; one for each device.

::

   c:\>inventory_advanced.py
   output: '15.2(4)S5'
   output: '2.5.5.47'

   Result:
   '['2.5.5.47', '15.2(4)S5']'

   c:\>

Hidden password
***************

This chapter is not specific to netscud. It explain how to use netscud with a login and a password not stored in a netscud script without using inventory. Other solution like using vault can be used but here is just a simple practical example.

The idea is simple: the credentials are stored into a file. This file should not be accessible by unauthorized users or included in git repository.

Here is the file with credentials "credentials.txt":

::

   ciscologin
   ciscopassword

As you see this is very simple: the first line contains the login of your device and the second line contains the password of your network device. The values must be adapted according to your device.

The script to read the credentials is the following:

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      # Read a text file with 2 lines: 1 with a login and the other one with a password
      with open("credentials.txt") as f:
         credentials = f.read()

      # Extract the 2 data from the text read
      (login, password) = credentials.split()

      # Variable declaration with the login and password read
      my_device = {
         "ip": "192.168.0.2",
         "username": login,
         "password": password,
         "device_type": "cisco_s300",
      }

      # Creation of a device
      async with netscud.ConnectDevice(**my_device) as device:

         # Sending command
         output = await device.send_command("show vlan")

         # Display message
         print(output)


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())

**Explanation:**

First the file "credentials.txt" is read and the content of the file is stored into a variable: credentials.

.. code-block:: Python

   # Read a text file with 2 lines: 1 with a login and the other one with a password
   with open("credentials.txt") as f:
      credentials = f.read()

Login and password are separated from the string variable credentials and stored into login and variable password respectively.

.. code-block:: Python

   # Extract the 2 data from the text read
   (login, password) = credentials.split()

Finally the login and password variables are used for the username and password parameters of a device. Then the script can run the same way as usual.

.. code-block:: Python

   # Variable declaration with the login and password read
   my_device = {
      "ip": "192.168.0.2",
      "username": login,
      "password": password,
      "device_type": "cisco_s300",
   }

The result of the script is:

::

   c:\>hidden_password.py
   Created by: D-Default, S-Static, G-GVRP, R-Radius Assigned VLAN, V-Voice VLAN

   Vlan       Name           Tagged Ports      UnTagged Ports      Created by
   ---- ----------------- ------------------ ------------------ ----------------
   1           1                             gi1-7,gi9,Po1-8          DV
   2          MAN                                gi8,gi10             S

   c:\>

Special prompt
**************

In some cases it can be useful to answer to a question a network device is asking from a command.

Thus in Cisco SG3XX device it can be necessary to answer to a yes/no question.

Here is an example:

::

   switch#wr
   Overwrite file [startup-config].... (Y/N)[N] ?N

   switch#

If we send a send_command() as usual it will end with a time out because this command expect to get a prompt return; here it would be "switch#" which does not exist in the string "Overwrite file [startup-config].... (Y/N)[N] ?".

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      my_device = {
         "ip": "192.168.0.2",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_s300",
      }

      # Creation of a device
      async with netscud.ConnectDevice(**my_device) as sw1:

         # Command to send
         cmd = "write memory"

         # Special pattern (from "Overwrite file [startup-config].... (Y/N)[N] ?")
         pattern = "?"

         # Sending command
         output = await sw1.send_command(cmd, pattern)

         # Command to send
         cmd = "y"

         # Sending command
         output += await sw1.send_command(cmd)

         # Display message
         print(output)


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())

**Explanation:**

The solution is to use a special parameter in the send_command() command.

First in addition to the command we use a second parameter here called pattern with the expected string pattern or the end of this pattern.

.. code-block:: Python

   # Command to send
   cmd = "write memory"

   # Special pattern (from "Overwrite file [startup-config].... (Y/N)[N] ?")
   pattern = "?"

   # Sending command
   output = await sw1.send_command(cmd, pattern)

Then the second command is just answering the device answer.

.. code-block:: Python

         # Command to send
         cmd = "y"

         # Sending command
         output += await sw1.send_command(cmd)

The result of the script is the following:

::

   c:\>special_prompt.py
   Overwrite file [startup-config].... (Y/N)[N] ?Y
   06-Oct-2020 22:08:32 %COPY-I-FILECPY: Files Copy - source URL running-config destination URL flash://system/configuration/startup-config
   06-Oct-2020 22:08:33 %COPY-N-TRAP: The copy operation was completed successfully


   c:\>

Telnet simple
*************

Async Telnet is supported by netscud even though it is not a secure protocol.

.. code-block:: Python

   # Python library import
   import asyncio, netscud


   async def task():
      """
      Async function
      """

      my_device = {
         "ip": "192.168.0.2",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_s300",
         "protocol": "telnet",
      }

      # Creation of a device
      async with netscud.ConnectDevice(**my_device) as sw1:

         # Command to send
         cmd = "show ip route"

         # Sending command
         output = await sw1.send_command(cmd)

         # Display message
         print(output)


   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(task())

As you can see the only difference with SSH connection is the "protocol" parameter in the definition of the device with the value "telnet". API and send_command() can be used as usual.

.. code-block:: Python

   my_device = {
      "ip": "192.168.0.2",
      "username": "cisco",
      "password": "cisco",
      "device_type": "cisco_s300",
      "protocol": "telnet",
   }

The result given is:

::

   c:\>telnet_simple.py
   Maximum Parallel Paths: 1 (1 after reset)
   IP Forwarding: enabled
   Codes: > - best, C - connected, S - static


   S   0.0.0.0/0 [1/4] via 192.168.0.1, 10:20:58, vlan 2
   C   192.168.0.0/24 is directly connected, vlan 2

   c:\>













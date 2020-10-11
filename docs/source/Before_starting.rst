Before starting
####################

Basic information
*****************

netscud uses 2 protocols to access a device:

* SSH
* Telnet

By default SSH is selected in the scripts.

The commands you send to the network device with netscud are the same as those someone can send using a terminal like Tera term or putty but it is sent programmatically using Python.

netscud uses asynchronous and non-blocking commands. So when connections and commands are in used they are not waiting (blocking) for the answer of the network devices. To achive this goal a event loop is used. This loop is managed by asyncio.

Asynchronous techniques are very interesting with I/O bound issues such as communcation with devices not only with SSH but also with other protocols.

The commands with asyncio are not always easy to write since the structure of an asynchronous program is different than a synchronous program. That is why the tutorial gradually shows how to write those programs properly till the gather() function.

Every scripts start with the declaration of asyncio library and netscud. The first is needed for the ability to use async code and the second is for network device access.

.. code-block:: Python

   # Python library import
   import asyncio, netscud

What is more every script needs to run a code that executes an asynchronous function. This asynchronous function will allow asynchronous instruction (which use keywords such as "async" and "await").

In this example a script run the asynchronous function task():

.. code-block:: Python
    
    # Main async loop
    asyncio.run(task())

The asynchronous function is similar to other function but requires the keyword "async" at the beginning of the definition:

.. code-block:: Python

   async def task():
      
      ...


The non-blocking instructions are using "await" keyword. They will be activated or release with the event loop running in the background of the script. Those specific function are for connection and sending command with devices.

Here is an example of a command using "await" inside an async function:

.. code-block:: Python

    # Sending command
    output = await my_switch.send_command("show ip int br)

This command send the command "show ip int br" to a router and give the hand to another await command if needed. Then when the answer is available it return the result of the command into the "output" variable.


Supported devices
*****************

Right now the following devices are supported:

::

    - Cisco IOS
    - Cisco SG3XX
    - Alcatel AOS
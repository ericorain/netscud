.. netscud documentation master file, created by
   sphinx-quickstart on Thu Oct  8 07:19:56 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to netscud's documentation!
===================================


.. image:: _static/pict/pict01.png
   :align:   center

netscud is an SSH and Telnet python library for network devices (mainly network switches and routers). It uses async techniques to speed up concurrent connections.

As an overview here is an example of netscud code for a Cisco IOS device:

.. code-block:: Python

   # Python library import
   import asyncio, netscud

   async def main():

      # Device parameters
      my_device = {
         "ip": "192.168.0.16",
         "username": "cisco",
         "password": "cisco",
         "device_type": "cisco_ios",
      }

      # Creation of a device
      async with netscud.ConnectDevice(**my_device) as sw1:

         # Sending command
         output = await sw1.send_command("show interfaces description")

         # Display message
         print(output)

   # Main function call
   if __name__ == "__main__":

      # Main async loop
      asyncio.run(main())

The result of this script is:

::

   c:\>script.py
   Interface              IP-Address      OK? Method Status                Protocol
   FastEthernet0/0        192.168.0.16    YES NVRAM  up                    up
   FastEthernet0/1        unassigned      YES manual up                    up
   FastEthernet1/0        unassigned      YES manual administratively down down
   FastEthernet1/1        unassigned      YES DHCP   up                    up
   Ethernet2/0            unassigned      YES DHCP   up                    up
   Ethernet2/1            unassigned      YES NVRAM  up                    up
   Ethernet2/2            unassigned      YES NVRAM  up                    up
   Ethernet2/3            unassigned      YES NVRAM  up                    up

   c:\>

If you are not afraid by this first script then what is following is for you.


.. toctree::
   :maxdepth: 1
   :caption: Contents:
   :numbered:

   Installation
   Before_starting
   Tutorial
   API
   FAQ


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

# netscud

netscud is an SSH and Telnet python library for network devices (mainly network switches and routers). It uses async techniques to speed up concurrent connections.

As an overview here is an example of netscud code for a Cisco IOS device:


```python
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
```

The result of this script is:

```bat
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
```

Documentation can be found here: https://netscud.readthedocs.io/en/latest/

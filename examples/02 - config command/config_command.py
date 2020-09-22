# Python library import
import asyncio, netscud

async def task():
    """
    Async function
    """

    my_device = {
        'ip':   '192.168.0.16',
        'username': 'cisco',
        'password': 'cisco',
        'device_type': 'cisco_ios',
    }



    # Connection to the device
    sw1 = await netscud.ConnectDevice(**my_device)

    # Commands to send
    cmds = ["interface FastEthernet1/0",
            "ip address 1.1.1.1 255.255.255.0",
            "no shutdown",
    ]

    # Sending command
    output = await sw1.send_config_set(cmds)

    # Display message
    print(output)
    
    # Disconnection
    await sw1.disconnect()



# Main function call 
if __name__ == '__main__':

    # Main async loop
    asyncio.run(task())


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

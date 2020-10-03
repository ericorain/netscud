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

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

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

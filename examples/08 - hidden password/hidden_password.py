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

# Python library import
import asyncio, netscud

# from netscud import Inventory
from netscud.inventory import Inventory


async def run_client(**host):
    """
    async function used by each device individually

    """
    output = ""

    try:

        # Connection to the device
        device = await netscud.ConnectDevice(**host)

        # Sending command
        output = await device.get_version()

        # Display message
        print("output: '" + str(output) + "'")

    except:

        pass

    # If a connection is active then when can disconnect the device
    if "device" in locals():

        # Disconnection of the device
        await device.disconnect()

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

    # Run the tasks
    result = await asyncio.gather(*tasks)

    # Display message
    print("\nResult:\n'" + str(result) + "'")


# Main function call
if __name__ == "__main__":

    # Main async loop
    asyncio.run(main_task())

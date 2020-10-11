# Python library import
import asyncio, netscud

# from netscud import Inventory
from netscud.inventory import Inventory


async def run_client(**host):
    """
    async function used by each device individually

    """

    # Default returned value
    output = ""

    try:

        # Connection to the device
        async with netscud.ConnectDevice(**host) as device:

            # Sending command
            output = await device.get_version()

            # Display message
            print("output: '" + str(output) + "'")

    except:

        # If something is wrong then an error message is displayed
        print("Error")

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

    # Run the tasks concurrently and collect the results
    result = await asyncio.gather(*tasks)

    # Display message
    print("\nResult:\n'" + str(result) + "'")


# Main function call
if __name__ == "__main__":

    # Main async loop
    asyncio.run(main_task())

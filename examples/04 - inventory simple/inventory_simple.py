# Python library import
import asyncio, netscud

# from netscud import Inventory
from netscud.inventory import Inventory


async def main_task():
    """
    Async main function
    """

    # Create an inventory with the devices from yaml file
    My_inventory = Inventory()

    # Get the list of all devices from the inventory
    my_devices = My_inventory.get_all_devices()

    # Display message
    print("All the devices:")

    # Display the devices one by one
    for device in my_devices:
        print(device)

    # Get the list of some devices from the inventory
    my_devices = My_inventory.select(device_type="cisco_ios")

    # Display message
    print("\nCisco IOS devices:")

    # Display the devices one by one
    for device in my_devices:
        print(device)


# Main function call
if __name__ == "__main__":

    # Main async loop
    asyncio.run(main_task())

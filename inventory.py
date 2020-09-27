# Python library import
import yaml, logging

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.WARNING)


class Inventory:
    """
    Class used to read inventory yaml file and select devices that will receive commands

    """

    def __init__(self, **kwargs):

        self.all_devices = []
        self.yaml_host_file_dict = {}

        # File to open
        hosts_file = r"d:\Prog\python\git\netscud\inventory\hosts.yaml"

        # Display info message
        logging.info("Inventory: reading file '" + str(hosts_file) + "'")

        try:
            # Open hosts.yaml file
            with open(hosts_file) as stream:

                # Get yaml data
                self.yaml_host_file_dict = yaml.safe_load(stream)

        except OSError:

            # Error while opening the file

            # Display info message
            logging.info("Error while opening file " + hosts_file)

            raise

        # Display info message
        logging.info(
            "Inventory: reading file '"
            + str(hosts_file)
            + "' data:\n'"
            + str(self.yaml_host_file_dict)
            + "'"
        )

        # Convert yaml file data (dict) into a list of devices
        self.all_devices = self.convert_yaml_to_list(self.yaml_host_file_dict)

        # Display info message
        logging.info("Inventory: all_devices:\n'" + str(self.all_devices) + "'")

    def convert_yaml_to_list(self, input_data):
        """
        Build a list from yaml data (dictionary)


        """

        """
        # No data?
        if input_data == None and self.all_devices:
            
            # Yes, no data

            # Then all the devices are selected
            input_data = self.all_devices
        """

        # By default no devices
        list_of_devices = []

        # Read all devices from yaml extracted data
        for device in input_data:

            device_dict = {**input_data[device], **{"name": device}}

            # Display info message
            logging.info(
                "convert_yaml_to_list: device dict: '" + str(device_dict) + "'"
            )

            # Add the dictionary of a device into a list
            list_of_devices.append(device_dict)

        return list_of_devices

    def get_all_devices(self):
        """
        Get all devices in a list



        """

        # By default no devices
        list_of_devices = []

        # Some devices?
        if self.all_devices:

            # Yes

            # Get the devices
            list_of_devices = self.all_devices

        return list_of_devices


# Main function call
if __name__ == "__main__":

    inv = Inventory()

    print("Get_devices:")

    for device in inv.get_all_devices():
        print("Device :\n" + str(device))

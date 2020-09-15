
# Python library import
import yaml, logging

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.WARNING)

class Inventory:
    """
    Class used to read inventory yaml file and select devices that will receive commands

    """

    def __init__(self, **kwargs):

        self.all_devices = []
        self.yaml_host_file_dict = {}

        # File to open
        hosts_file = r"d:\Prog\python\git\netscud\hosts.yaml"



        try:
            # Open hosts.yaml file
            with open(hosts_file) as stream:
                
                # Get yaml data
                self.yaml_host_file_dict = yaml.safe_load(stream)

        except OSError:

            # Error while opening the file

            # Display info message
            logging.info("Error while opening file " + hosts_file)

        else:
            # Display info message
            logging.info("Reading " + str(hosts_file) + " file:\n'" + str(self.yaml_host_file_dict) + "'")


    def build(self, **kwargs):
        """
        Build a list from yaml data


        """

        pass


# Main function call 
if __name__ == '__main__':

    Inventory()

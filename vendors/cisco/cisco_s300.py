# Python library import
from netscud.base_connection import NetworkDevice
import logging

class CiscoS300(NetworkDevice):
    """
    Class for SG3XX devices
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self._telnet_connect_login = "User Name:"
        self._telnet_connect_password = "Password:"
        self._telnet_connect_authentication_fail_prompt = ["User Name:","authentication failed"]
        self.cmd_disable_paging = "terminal datadump"
        self.cmd_get_serial_number = "show system id unit 1"



    async def get_version(self):
        """
        Asyn method used to get the version of the software of the device

        :return: Version of the software of the device
        :rtype: str
        """

        # Display info message
        logging.info("get_version")

        # By default empty string
        version = ""

        # Run get version on the device
        output = await self.send_command(self.cmd_get_version)

        # Seek "Version: " on each line of the returned output
        for line in output.splitlines():

            logging.info("get_version: line: " + line)

            # Is it the line with "Version: "
            if "Version: " in line:

                # Yes

                # Then take the version from this line
                version = line.split("Version: ")[1]

                # Break the loop
                break

        # Display info message
        logging.info("get_version: version: " + version)

        # Return the version of the software of the device
        return version


    async def save_config(self):
        """
        Asyn method used to save the current configuration on the device

        :return: Commands of the configuration saving process
        :rtype: str
        """

        # Display info message
        logging.info("save_config")

        # Send command to ask for saving config. Wait till the question to overwrite
        # the startup file ("Overwrite file [startup-config].... (Y/N)[N] ?")
        output = await self.send_command(self.cmd_save_config, pattern="?")

        # Confirm to save the config
        output += await self.send_command("Y")

        # Return the commands of the configuration saving process
        return output

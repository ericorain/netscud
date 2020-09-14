# Python library import
from netscud.base_connection import NetworkDevice
import logging

class AlcatelAOS(NetworkDevice):
    """
    Class for Alcatel AOS devices
    """



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._connect_first_ending_prompt = ["-> ", "> "]
        self.list_of_possible_ending_prompts = ["> "]
        self.cmd_disable_paging = ""
        self.cmd_enter_config_mode = ""
        self.cmd_exit_config_mode = ""
        self.cmd_get_version = "show microcode"
        self.cmd_get_hostname = "show system"
        self.cmd_get_model = "show chassis"
        self.cmd_get_serial_number = "show chassis"
        self.cmd_get_config = "show configuration snapshot"
        self.cmd_save_config = ["write memory","copy running certified"]

        """
        b065net - DOP-PF ==> wr mem

        File /flash/vcdir_841R03/vcsetup.cfg replaced.

        File /flash/vcdir_841R03/vcboot.cfg replaced.

        b065net - DOP-PF ==> copy running certified
        Please wait...


        b065net - DOP-PF ==>
        """


    async def get_hostname(self):
        """
        Asyn method used to get the name of the device

        :return: Name of the device
        :rtype: str
        """

        # Display info message
        logging.info("get_hostname")

        # Get hostname
        output = await self.send_command(self.cmd_get_hostname)

        # Display info message
        logging.info("get_hostname: output: '" + str(output) + "'")

        # By default no hostname
        hostname = ""

        # Check all line of the returned hostname command
        for line in output.splitlines():

            # Is "Name: " part of the line?
            if "Name: " in line:
                
                # Yes

                # Extract the hostname of the same line
                hostname = line.split()[-1][:-1]

                # Leave the loop
                break

        # Display info message
        logging.info("get_hostname: hostname found: '" + str(hostname) + "'")

        # Return the name of the device
        return hostname


    async def get_model(self):
        """
        Asyn method used to get the model of the device

        :return: Model of the device
        :rtype: str
        """

        # Display info message
        logging.info("get_model")

        # Get model
        output = await self.send_command(self.cmd_get_model)

        # Display info message
        logging.info("get_model: output: '" + str(output) + "'")

        # By default no model
        model = ""

        # Check all line of the returned hostname command
        for line in output.splitlines():

            # Is "Model Name:" part of the line?
            if "Model Name:" in line:
                
                # Yes

                # Extract the hostname of the same line
                model = line.split()[-1][:-1]

                # Leave the loop
                break

        # Display info message
        logging.info("get_model: model found: '" + str(model) + "'")

        # Return the model of the device
        return model


    async def get_serial_number(self):
        """
        Get serial number of the switch or the serial number of the first switch of a stack

        :return: Serial number of the device
        :rtype: str
        """

        # Display info message
        logging.info("get_serial_number")

        # Get model
        output = await self.send_command(self.cmd_get_serial_number)

        # Display info message
        logging.info("get_serial_number: output: '" + str(output) + "'")

        # By default no serial number
        serial_number = ""

        # Check all line of the returned hostname command
        for line in output.splitlines():

            # Is "Serial Number:" part of the line?
            if "Serial Number:" in line:
                
                # Yes

                # Extract the hostname of the same line
                serial_number = line.split()[-1][:-1]

                # Leave the loop
                break

        # Display info message
        logging.info("get_serial_number: serial number found: '" + str(serial_number) + "'")

        # Return the serial number of the device
        return output



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

        # Get the version from the output returned 
        version = output.splitlines()[3].split()[1]

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

        # By default no returned data
        output = ""

        # Send commands for saving config
        for cmd in self.cmd_save_config:
            output += await self.send_command(cmd)

        # Return
        return output
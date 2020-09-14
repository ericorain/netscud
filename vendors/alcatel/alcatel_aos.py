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
        self._telnet_connect_login = "login :"
        self._telnet_connect_password = "password :"
        self._telnet_connect_authentication_fail_prompt = ["login :","Authentication failure"]
        self.cmd_disable_paging = ""
        self.cmd_enter_config_mode = ""
        self.cmd_exit_config_mode = ""
        self.cmd_get_version = "show microcode"
        self.cmd_get_hostname = "show system"
        self.cmd_get_model = "show chassis"
        self.cmd_get_serial_number = "show chassis"
        self.cmd_get_config = "show configuration snapshot"
        self.cmd_save_config = ["write memory", # Save data into working configuration
                                "copy running certified", # AOS 7, AOS 8, save working configuration into certified configuration
                                "copy working certified" # AOS 6 and lower, save working configuration into certified configuration
        ]


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

        Alcatel switch can be very slow while copying configuration. Consider to temporary
        change the time out of the command (using "self.timeout" variable) before running
        this method.
        By default the timer is temporary increased by 60 seconds

        :return: Commands of the configuration saving process
        :rtype: str
        """

        # Display info message
        logging.info("save_config")

        # Time out increased
        self.timeout += 60

        # By default no returned data
        output = ""

        # Send commands for saving config

        # Command to send
        cmd = self.cmd_save_config[0]

        # Save data into working configuration
        output += await self.send_command(cmd)

        # Add carriage return to the output
        output += "\n"

        # Command to send
        cmd = self.cmd_save_config[1]

        # AOS 7, AOS8, save working configuration into certified configuration
        data = await self.send_command(cmd)

        # An error with the previous command happened (i.e the command is not supported by the switch)?
        if ('ERROR: Invalid entry: "running"') in data:

            # Yes

            # Then try to save ce configuration with another command

            # Display info message
            logging.warning("save_config: '" + self.cmd_save_config[1] + "' command not supported. Trying another 'copy' command: '" + self.cmd_save_config[2] + "'")

            # Add carriage return to the output
            output += "\n"

            # Command to send
            cmd = self.cmd_save_config[2]

            # AOS 6 and lower, save working configuration into certified configuration
            output += await self.send_command(cmd)
        
        else:

            # No

            # So result can be saved into the output
            output += data


        # Time out restored
        self.timeout -= 60


        # Return the commands of the configuration saving process
        return output


    async def send_config_set(self, cmds=None):
        """
        Async method used to send command in config mode

        There is no configuration mode with Alcatel AOS switches.
        So this command will just run a group of commands

        :param cmds: The commands to the device
        :type cmds: str or list

        :return: the results of the commands sent
        """

        # By default there is no output
        output = ""

        # Optional carriage return
        carriage_return = ""

        # Run each command
        for cmd in cmds:

            # Add carriage return if needed (first time no carriage return)
            output += carriage_return

            # Send a command
            output+= await self.send_command(cmd)

            # Set carriage return for next commands
            carriage_return = "\n"

        # Return the commands sent
        return output

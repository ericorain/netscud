# Python library import
from netscud.base_connection import NetworkDevice, log


class MikrotikRouterOS(NetworkDevice):
    """
    Class for Mikrotik RouterOS devices
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove useless escape data using the user login
        self.username = self.username + "+ct"

        self._connect_first_ending_prompt = ["> \x1b[K"]
        self.list_of_possible_ending_prompts = [
            "> ",
        ]
        # No global disabling for Mikrotik RouterOS so use
        # "without-paging" at the end of your commands
        self.cmd_disable_paging = None

        self.cmd_exit_config_mode = "quit"
        self.cmd_get_version = "system resource print without-paging"
        self.cmd_get_hostname = "system identity print without-paging"
        self.cmd_get_model = "system resource print without-paging"
        self.cmd_get_serial_number = "system routerboard print without-paging"
        self.cmd_get_config = "export"
        self.cmd_get_mac_address_table = "interface bridge host print without-paging"
        # No command to save the config. So it is always saved after "Enter"
        self.cmd_save_config = ""

    async def send_config_set(self, cmds=None, timeout=None):
        """
        Async method used to send command in config mode

        There is no configuration mode with Mikrotik RouterOS switches.
        So this command will just run a group of commands

        :param cmds: The commands to the device
        :type cmds: str or list

        :param timeout: optional, a timeout for the command sent. Default value is self.timeout
        :type timeout: str

        :return: the results of the commands sent
        :rtype: list of str
        """

        # Display info message
        log.info("send_config_set")

        # Default value of timeout variable
        if timeout is None:
            timeout = self.timeout

        # By default there is no output
        output = ""

        # Optional carriage return
        carriage_return = ""

        # Check if cmds is a string
        if isinstance(cmds, str):

            # A string

            # Convert the string into a list
            cmds = [cmds]

            # A list?
        elif not isinstance(cmds, list):

            # Not a list (and not a string)

            # Display error message
            log.error(
                "send_config_set: parameter cmds used in send_config_set is neither a string nor a list"
            )

            # Leave the method
            return output

        # Run each command
        for cmd in cmds:

            # Add carriage return if needed (first time no carriage return)
            output += carriage_return

            # Send a command
            output += await self.send_command(cmd)

            # Set carriage return for next commands
            carriage_return = "\n"

        # Return the commands sent
        return output

    #########################################################
    #
    # List of API
    #
    #########################################################

    async def get_version(self):
        """
        Asyn method used to get the version of the software of the device

        :return: Version of the software of the device
        :rtype: str
        """

        # Display info message
        log.info("get_version")

        # By default empty string
        version = ""

        # Run get version on the device
        output = await self.send_command(self.cmd_get_version)

        # Seek data to get the version in the returned output
        version = output.split("version: ")[1].split()[0]

        # Display info message
        log.info(f"get_version: version: {version}")

        # Return the version of the software of the device
        return version

    async def get_hostname(self):
        """
        Asyn method used to get the name of the device

        :return: Name of the device
        :rtype: str
        """

        # Display info message
        log.info("get_hostname")

        # Get hostname
        output = await self.send_command(self.cmd_get_hostname)

        # Display info message
        log.info(f"get_hostname: output: '{output}'")

        # Remove the useless information in the returned string
        output = output.split()[1]

        # Display info message
        log.info(f"get_hostname: hostname found: '{output}'")

        # Return the name of the device
        return output

    async def get_model(self):
        """
        Asyn method used to get the model of the device

        :return: Model of the device
        :rtype: str
        """

        # Display info message
        log.info("get_model")

        # Get model
        output = await self.send_command(self.cmd_get_model)

        # Display info message
        log.info(f"get_model: output: '{output}'")

        # Remove the useless information in the returned string
        output = output.split("board-name: ")[1].split()[0]

        # Display info message
        log.info(f"get_model: model found: '{output}'")

        # Return the model of the device
        return output

    async def get_serial_number(self):
        """
        Get serial number of the switch or the serial number of the first switch of a stack

        :return: Serial number of the device
        :rtype: str
        """

        # Display info message
        log.info("get_serial_number")

        # Get model
        output = await self.send_command(self.cmd_get_serial_number)

        # Display info message
        log.info(f"get_serial_number: output: '{output}'")

        # Remove the useless information in the returned string
        output = output.split("serial-number: ")[1].split()[0]

        # Display info message
        log.info(f"get_hostname: hostname found: '{output}'")

        # Return the serial number of the device
        return output

    async def get_config(self, timeout=None):
        """
        Asyn method used to get the configuration of the device

        :param timeout: optional, a timeout for the command sent. Default value is self.timeout
        :type timeout: str

        :return: Configuration of the device
        :rtype: str
        """

        # Display info message
        log.info("get_config")

        # Default value of timeout variable
        if timeout is None:
            timeout = self.timeout

        # Get config
        output = await self.send_command(self.cmd_get_config, timeout=timeout)

        # Return de configuration of the device
        return output

    async def save_config(self):
        """
        Asyn method used to save the current configuration on the device

        :return: Commands of the configuration saving process
        :rtype: str
        """

        # Display info message
        log.info("save_config")

        # No need to send a commmand
        output = ""

        # Return the commands of the configuration saving process
        return output

    async def get_mac_address_table(self):
        """
        Asyn method used to get the mac address table of the device

        :return: Configuration of the device
        :rtype: list of dict
        """

        # Display info message
        log.info("get_mac_address_table")

        # By refault nothing is returned
        returned_output = []

        # Get config
        output = await self.send_command(self.cmd_get_mac_address_table)

        # Convert string to list of string and remove the 2 first lines
        lines = output.splitlines()[2:]

        # Read each line
        for line in lines:

            # Get the type of MAC address (dynamic or static)
            if line[5].lower() == "d":

                # Dynamic MAC address
                mac_type = "dynamic"
            else:

                # Static MAC address
                mac_type = "static"

            # Get MAC address
            mac_address = line[9:26]

            # Get VLAN
            vlan = line[27:31].strip()

            # Get interface
            interface = line[32:].split()[0]

            # Create a dictionary
            mac_dict = {
                "mac_type": mac_type,
                "mac_address": mac_address,
                "vlan": vlan,
                "interface": interface,
            }

            # Add the MAC information to the list
            returned_output.append(mac_dict)

        # Return de configuration of the device
        return returned_output
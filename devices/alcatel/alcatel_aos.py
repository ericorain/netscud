# Python library import
from netscud.base_connection import NetworkDevice, log


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
        self._telnet_connect_authentication_fail_prompt = [
            "login :",
            "Authentication failure",
        ]

        # General commands
        self.cmd_disable_paging = ""
        self.cmd_enter_config_mode = ""
        self.cmd_exit_config_mode = ""
        self.cmd_get_version = "show microcode"
        self.cmd_get_hostname = "show system"
        self.cmd_get_model = "show chassis"
        self.cmd_get_serial_number = "show chassis"
        self.cmd_get_config = "show configuration snapshot"
        self.cmd_save_config = [
            "write memory",  # Save data into working configuration
            "copy running certified",  # AOS 7, AOS 8, save working configuration into certified configuration
            "copy working certified",  # AOS 6 and lower, save working configuration into certified configuration
        ]

        # Layer 1 commands
        self.cmd_get_interfaces = [
            "show interfaces",
            "show interfaces alias",  # AOS 7, AOS 8
            "show interfaces port",  # AOS 6 and lower
            "show vlan members",  # AOS 7, AOS 8
            "show vlan port",  # AOS 6 and lower
        ]

        # Layer 2 commands

        # Layer 3 commands

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
        log.info(f"get_hostname: hostname found: '{hostname}'")

        # Return the name of the device
        return hostname

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
        log.info(f"get_model: model found: '{model}'")

        # Return the model of the device
        return model

    async def get_serial_number(self):
        """
        Get serial number of the switch or the serial number of the first switch of a stack

        :return: Serial number of the device
        :rtype: str
        """

        # Display info message
        log.info("get_serial_number")

        # Get serial number
        output = await self.send_command(self.cmd_get_serial_number)

        # Display info message
        log.info(f"get_serial_number: output: '{output}'")

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
        log.info(f"get_serial_number: serial number found: '{serial_number}'")

        # Return the serial number of the device
        return output

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

        # Get the version from the output returned
        version = output.splitlines()[3].split()[1]

        # Display info message
        log.info(f"get_version: version: {version}")

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
        log.info("save_config")

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
            log.warning(
                f"save_config: '{self.cmd_save_config[1]}' command not supported. Trying another 'copy' command: '{self.cmd_save_config[2]}'"
            )

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

    async def send_config_set(self, cmds=None, timeout=None):
        """
        Async method used to send command in config mode

        There is no configuration mode with Alcatel AOS switches.
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
            output += await self.send_command(cmd, timeout)

            # Set carriage return for next commands
            carriage_return = "\n"

        # Return the commands sent
        return output

    async def get_interfaces(self):
        """
        Asyn method used to get the information of ALL the interfaces of the device

        some commands are used to collect interface data:
        - one for status
        - one for duplex/speed
        - one for mode (access / trunk / hybrid)

        The returned dictionaries inside the dictionary will return that information:

                returned_dict = {
                    "operational": operational,
                    "admin_state": admin_state,
                    "maximum_frame_size": maximum_frame_size,
                    "full_duplex": full_duplex,
                    "speed": speed,
                    "mode": mode,
                    "description": description,
                }

        :return: Interfaces of the device
        :rtype: dict of dict
        """

        # Display info message
        log.info("get_interfaces")

        # By default nothing is returned
        returned_output = {}

        # self.cmd_get_interfaces = [
        #     "show interfaces",
        #     "show interfaces alias", # AOS 7, AOS 8
        #     "show interfaces port",  # AOS 6 and lower
        #     "show vlan members",     # AOS 7, AOS 8
        #     "show vlan port",        # AOS 6 and lower
        # ]

        # Command for the status of the interfaces

        # Send a command
        output_status = await self.send_command(self.cmd_get_interfaces[0])

        # Display info message
        log.info(f"get_interfaces: status command\n'{output_status}'")

        # Command for the description of the interfaces

        # Send a command
        output_description = await self.send_command(self.cmd_get_interfaces[1])

        # Check if the returned value is not having an error (AOS 6 does has another command)
        # Error message should be:
        #                                                ^
        # ERROR: Invalid entry: "alias"
        if "error" in output_description.lower():

            # Yes, the command returns an error

            # Display info message
            log.info(
                f"get_interfaces: description command: error:\n'{output_description}'"
            )

            # So let's try to send an AOS 6 equivalent command

            # Send a command
            output_description = await self.send_command(self.cmd_get_interfaces[2])

        # Display info message
        log.info(f"get_interfaces: description command\n'{output_description}'")

        # Command for the mode of the interfaces (access or trunk)

        # Send a command
        output_mode = await self.send_command(self.cmd_get_interfaces[3])

        # Check if there is an error message like this one:
        #                                         ^
        # ERROR: Invalid entry: "members"
        #
        if "error" in output_mode.lower():
            # Yes

            # Display info message
            log.info(f"get_interfaces: mode command: error:\n'{output_mode}'")

            # Then an older command will be used

            # Command for the mode of the interfaces (access or trunk)

            # Send a command
            output_mode = await self.send_command(self.cmd_get_interfaces[4])

        # Display info message
        log.info(f"get_interfaces: mode command\n'{output_mode}'")

        ############################################
        # Research of trunk
        ############################################

        # Convert output_description into a list of lines
        list_output_mode_data = output_mode.splitlines()

        # By default the description dictionary is empty
        dict_mode = {}

        # By default the lines read are header
        no_header_data = False

        # Read each line to find data (mode)
        for line in list_output_mode_data:

            # Is it the header data without information about interfaces?
            if not no_header_data:

                # Yes

                # Let's check if it is still the case
                if line.startswith("---"):

                    # Next time it will be interface data
                    no_header_data = True

            else:

                # Initialize data with default values
                interface_name = ""
                mode = "access"

                # Data after header = interface information

                # Get interface name and admin state
                interface_and_mode = line.split()

                # Check if there are 3 values at least (i.e. vlan, interface and mode)
                if len(interface_and_mode) > 3:

                    # Yes, there are 3 values at least

                    # Check if the interface is have type "qtagged"
                    if interface_and_mode[2] == "qtagged":

                        # Yes, it is a trunk

                        # Extract interface name
                        interface_name_possible = interface_and_mode[1]

                        # Check now if the interface name has "/" in the string
                        if "/" in interface_name_possible:

                            # Yes it has

                            # So save the name of the interface
                            interface_name = interface_name_possible

                            # Save data into the descrition dictionary
                            dict_mode[interface_name] = {
                                "mode": "trunk",
                            }

        # Display info message
        log.info(f"get_interfaces: dict_mode:\n'{dict_mode}'")

        # return dict_mode

        ############################################
        # Research of admin status and description
        ############################################

        # Convert output_description into a list of lines
        list_output_description_data = output_description.splitlines()

        # By default the description dictionary is empty
        dict_description = {}

        # By default the lines read are header
        no_header_data = False

        # Read each line to find data (admin status and description)
        for line in list_output_description_data:

            # Is it the header data without information about interfaces?
            if not no_header_data:

                # Yes

                # Let's check if it is still the case
                if line.startswith("---"):

                    # Next time it will be interface data
                    no_header_data = True

            else:

                # Data after header = interface information

                # Initialize data with default values
                interface_name = ""
                admin_state = False
                description = ""

                # Get interface name and admin state
                interface_and_admin_state = line.split()

                # Check if there are 2 values (i.e. an interface and an admin state are in the data)
                if len(interface_and_admin_state) >= 2:

                    # Yes, there are 2 values at least

                    # Extract interface name
                    interface_name_possible = interface_and_admin_state[0]

                    # Check now if the interface name has "/" in the string
                    if "/" in interface_name_possible:

                        # Yes it has

                        # So save the name of the interface
                        interface_name = interface_name_possible

                        # Extract admin state
                        admin_state_string = interface_and_admin_state[1]

                        # Check if admin state is "en" or "enable"
                        if "en" in admin_state_string:

                            # Admin state is enable
                            admin_state = True

                        # Now let's extract the description
                        # Only the first 40 characters are gathered
                        description = line.split('"', 1)[1].rsplit('"', 1)[0]

                        # Save data into the descrition dictionary
                        dict_description[interface_name] = {
                            "admin_state": admin_state,
                            "description": description,
                        }

        # Display info message
        log.info(f"get_interfaces: dict_description:\n'{dict_description}'")

        # return dict_description

        ############################################
        # Research of interface name, operational status,
        # duplex and speed
        ############################################

        # Let's convert the whole data of output_status into a list of data
        # Each list has data of 1 single interface (excluding first element)
        list_interfaces_status_data = output_status.split("Port")[1:]

        # Read each block of data to get information (interface name, operational status,
        # duplex and speed)
        for block_of_strings_status in list_interfaces_status_data:

            # Initialize data with default values
            interface_name = ""
            operational = False
            admin_state = False
            maximum_frame_size = 0
            full_duplex = False
            speed = 0  # speed is in Mbit/s
            mode = "access"
            description = ""

            # print(block_of_strings_status.split()[0])

            # Split data block into lines
            lines = block_of_strings_status.splitlines()

            # Get interface name:
            interface_name = lines[0].split()[0]

            # Read each line
            for line in lines:

                # Check if "Operational Status" is found in a line
                if "Operational Status" in line:

                    # Yes

                    # Check if "up" is in the string also
                    if "up" in line:

                        # Yes

                        # So operational status is "up"
                        operational = True

                # Check if "BandWidth" is found in a line
                if "BandWidth" in line:

                    # Yes

                    # Get speed
                    speed_string = line.split(":")[1].split(",")[0].strip()

                    # Check if the data string is a numeric value
                    if speed_string.isnumeric():

                        # Yes it is a numeric value

                        # Convert the speed in integer
                        speed = int(speed_string)

                    # Check if "Full" for Full duplex is in the line
                    if "full" in line.lower():

                        # Yes

                        # Save Full duplex state
                        full_duplex = True

                # Check if "Long Frame Size(Bytes)" is found in a line
                if "Long Frame Size(Bytes)" in line:

                    # Yes

                    # Get Maximum Frame Size
                    maximum_frame_size_string = line.split(": ")[1].split(",")[0]

                    # Check if the data string is a numeric value
                    if maximum_frame_size_string.isnumeric():

                        # Yes it is a numeric value

                        # Convert the Maximum Frame Size in integer
                        maximum_frame_size = int(maximum_frame_size_string)

            # Check if the interface is present in dict_description
            if interface_name in dict_description:

                # Yes it is

                # Gathering admin state
                admin_state = dict_description[interface_name]["admin_state"]

                # Gathering description
                description = dict_description[interface_name]["description"]

            # Check if the interface is present in dict_mode (which means there is a trunk)
            if interface_name in dict_mode:

                # Yes, it is a trunk

                # Interface mode is "trunk"
                mode = "trunk"

            # Check if interface name is not empty
            if interface_name:

                # It is not empty

                # Create a dictionary
                returned_dict = {
                    "operational": operational,
                    "admin_state": admin_state,
                    "maximum_frame_size": maximum_frame_size,
                    "full_duplex": full_duplex,
                    "speed": speed,
                    "mode": mode,
                    "description": description,
                }

                # Add the information to the dict
                if interface_name:
                    returned_output[interface_name] = returned_dict

        # Return data
        return returned_output

    async def set_interface(
        self,
        interface=None,
        admin_state=None,
        description=None,
        maximum_frame_size=None,
        mode=None,
        **kwargs,
    ):
        """
        Asyn method used to set the state of an interface of the device


        :param interface: the name of the interface
        :type interface: str

        :param admin_state: optional, "up" or "down" status of the interface
        :type admin_state: bool

        :param description: optional, a description for the interface
        :type description: str

        :param maximum_frame_size: optional, L2 MTU for packets
        :type maximum_frame_size: int

        :param mode: optional, set the mode (access, trunk, hybrid) of the interface
        :type mode: str

        :param kwargs: not used
        :type kwargs: dict

        :return: Status. True = no error, False = error
        :rtype: bool
        """

        # Display info message
        log.info("set_interface")

        # By default result status is having an error
        return_status = False

        # Display info message
        log.info(f"set_interface: input: interface: {interface}")
        log.info(f"set_interface: input: admin_state: {admin_state}")
        log.info(f"set_interface: input: description: {description}")
        log.info(f"set_interface: input: maximum_frame_size: {maximum_frame_size}")
        log.info(f"set_interface: input: mode: {mode}")

        # No error
        return_status = True

        """
        interfaces 1/1 admin up
        interfaces 1/1/1 admin-state enable
        interfaces 1/1/1 alias ""
        interfaces 1/1/1 max-frame-size 1500
        interfaces 1/1 max frame 1500
        show configuration snapshot vlan
        vlan 310 members port 1/2/21 tagged
        vlan 229 port default 1/8
        vlan 229 802.1q 1/24 "TAG 1/24 VLAN 229"
        """

        # Return status
        return return_status
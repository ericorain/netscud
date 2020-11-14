# Python library import
from netscud.base_connection import NetworkDevice, log
import asyncio, asyncssh

# Declaration of constant values

# Max data to read in read function
MAX_BUFFER_DATA = 65535


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
        self.cmd_set_interface = [
            "interfaces <INTERFACE> admin-state enable",
            "interfaces <INTERFACE> admin-state disable",
            "interfaces <INTERFACE> admin up",
            "interfaces <INTERFACE> admin down",
            'interfaces <INTERFACE> alias "<DESCRIPTION>"',
            "interfaces <INTERFACE> max-frame-size <MAXIMUMFRAMESIZE>",
            "interfaces <INTERFACE> max frame <MAXIMUMFRAMESIZE>",
            "show vlan members",
            "show vlan port",
            "no vlan <VLAN> members port <INTERFACE>",
            "vlan <VLANLIST> no 802.1q <INTERFACE>",
            "show vlan",
        ]

        # Layer 2 commands

        # Layer 3 commands

    def monkey_patch_dsa_512(self):

        """
        Monkey patch that allows DSA 512 bits connections

        Code is ugly
        """

        import cryptography.hazmat.primitives.asymmetric.dsa

        def my_check_dsa_parameters(parameters):
            if parameters.p.bit_length() not in [512, 1024, 2048, 3072]:
                raise ValueError("p must be exactly 512, 1024, 2048, or 3072 bits long")
            if parameters.q.bit_length() not in [160, 224, 256]:
                raise ValueError("q must be exactly 160, 224, or 256 bits long")

        cryptography.hazmat.primitives.asymmetric.dsa._check_dsa_parameters = (
            my_check_dsa_parameters
        )

    async def connectSSH(self):
        """
        Async method used for connecting a device using SSH protocol
        """

        # Display info message
        log.info("connectSSH")

        # Monkey patch DSA 512 bits connections
        self.monkey_patch_dsa_512()

        # Parameters of the connection
        generator = asyncssh.connect(
            self.ip,
            username=self.username,
            password=self.password,
            known_hosts=None,
            # encryption_algs="*",  # Parameter that includes all encryption algorithms (even the old ones disabled by default)
            encryption_algs=[
                algs.decode("utf-8") for algs in asyncssh.encryption._enc_algs
            ],  # Parameter that includes all encryption algorithms (even the old ones disabled by default)
            # server_host_key_algs=["ssh-rsa", "ssh-dss"],
            server_host_key_algs=["ssh-dss"],
        )

        # Trying to connect to the device
        try:

            self.conn = await asyncio.wait_for(generator, timeout=self.timeout)

        except asyncio.exceptions.TimeoutError as error:

            # Timeout

            # Display error message
            log.error(f"connectSSH: connection failed: {self.ip} timeout: '{error}'")

            # Exception propagation
            raise asyncio.exceptions.TimeoutError(
                "Connection failed: connection timed out."
            )

        except Exception as error:

            # Connection failed

            # Display error message
            log.error(f"connectSSH: connection failed: {self.ip} '{error}'")

            # Exception propagation
            raise

        # Display info message
        log.info("connectSSH: connection success")

        # Create a session
        self.stdinx, self.stdoutx, _ = await self.conn.open_session(term_type="netscud")

        # Display info message
        log.info("connectSSH: open_session success")

        # By default no data has been read
        data = ""

        # By default no prompt found
        prompt_not_found = True

        try:

            # Read data
            while prompt_not_found:

                # Display info message
                log.info("connectSSH: beginning of the loop")

                # Read the prompt
                data += await asyncio.wait_for(
                    self.stdoutx.read(MAX_BUFFER_DATA), timeout=self.timeout
                )

                # Display info message
                log.info(f"connectSSH: data: '{str(data)}'")

                # Display info message
                log.info(f"connectSSH: data: hex:'{data.encode('utf-8').hex()}'")

                # Check if an initial prompt is found
                for prompt in self._connect_first_ending_prompt:

                    # Ending prompt found?
                    if data.endswith(prompt):

                        # Yes

                        # Display info message
                        log.info(f"connectSSH: first ending prompt found: '{prompt}'")

                        # A ending prompt has been found
                        prompt_not_found = False

                        # Leave the loop
                        break

                # Display info message
                log.info("connectSSH: end of loop")

        except Exception as error:

            # Fail while reading the prompt

            # Display error message
            log.error(
                f"connectSSH: timeout while reading the prompt: {self.ip} '{error}'"
            )

            # Exception propagation
            raise

        # Display info message
        log.info(f"connectSSH: end of prompt loop")

        # Remove possible escape sequence
        data = self.remove_ansi_escape_sequence(data)

        # Find prompt
        self.prompt = self.find_prompt(str(data))

        # Display info message
        log.info(f"connectSSH: prompt found: '{self.prompt}'")

        # Display info message
        log.info(f"connectSSH: prompt found size: '{len(self.prompt)}'")

        # Disable paging command available?
        if self.cmd_disable_paging:
            # Yes

            # Disable paging
            await self.disable_paging()

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

        """
        "interfaces <INTERFACE> admin-state enable",
        "interfaces <INTERFACE> admin-state disable",
        "interfaces <INTERFACE> admin up",
        "interfaces <INTERFACE> admin down",
        'interfaces <INTERFACE> alias "<DESCRIPTION>"',
        "interfaces <INTERFACE> max-frame-size <MAXIMUMFRAMESIZE>",
        "interfaces <INTERFACE> max frame <MAXIMUMFRAMESIZE>",
        "show vlan members",
        "show vlan port",
        "no vlan <VLAN> members port <INTERFACE>",
        "vlan <VLANLIST> no 802.1q <INTERFACE>",
        "show vlan",

        "show configuration snapshot vlan",
        "show configuration snapshot 802.1q",

        vlan 310 members port 1/2/21 tagged
        vlan 101 members port 1/2/21 untagged
        vlan 229 port default 1/8
        vlan 229 802.1q 1/24 "TAG 1/24 VLAN 229"

        # Alcatel AOS 7+
        vlan 101 members port 1/1/22 tagged
        vlan 110 members port 1/1/22 tagged
        no vlan 101 members port 1/1/22
        no vlan 110 members port 1/1/22

        # Alcatel AOS 6
        vlan 229 port default 1/7
        vlan 1 802.1q 1/7
        vlan 1 101 110 802.1q 1/7
        no 802.1q 1/7
        vlan 1 no 802.1q 1/7
        vlan 1 101 110 no 802.1q 1/7
        """

        # # Return status
        # return return_status

        # Get parameters

        # "interface" found?
        if interface == None:

            # No

            # So no action can be performed

            # Display info message
            log.info("set_interface: no interface specified")

            # Return status
            return return_status

        # "admin_state" found?
        if admin_state != None:

            # Yes

            # So admin state of the interface can be changed

            # Display info message
            log.info("set_interface: admin_state")

            # "up" or "down"? (True of False)
            if admin_state:

                # "up"

                # [ "interfaces <INTERFACE> admin-state enable", "interfaces <INTERFACE> admin-state disable",]

                # AOS 7+

                # Get the command
                cmd = self.cmd_set_interface[0]

            else:

                # "down"

                # Get the command
                cmd = self.cmd_set_interface[1]

            # Adapt the command line

            # Replace <INTERFACE> with the interface name
            cmd = cmd.replace("<INTERFACE>", interface)

            # Display info message
            log.info(f"set_interface: admin_state: cmd: {cmd}")

            # Change the state of the interface
            output = await self.send_command(cmd)

            # Check if there is an error (like whith AOS6)
            #                                               ^
            # ERROR: Invalid entry: "admin-state"
            if "admin-state" in output:

                # AOS 7+ command not supported

                # Display info message
                log.info(f"set_interface: admin_state command: error: {output}")

                # "up" or "down"? (True of False)
                if admin_state:

                    # "up"

                    # ["interfaces <INTERFACE> admin up","interfaces <INTERFACE> admin down",]

                    # AOS 6

                    # Get the command
                    cmd = self.cmd_set_interface[2]

                else:

                    # "down"

                    # Get the command
                    cmd = self.cmd_set_interface[3]

                # Adapt the command line

                # Replace <INTERFACE> with the interface name
                cmd = cmd.replace("<INTERFACE>", interface)

                # Display info message
                log.info(f"set_interface: admin_state: cmd: {cmd}")

                # Change the state of the interface
                output = await self.send_command(cmd)

            # An error (maybe a second time)?
            if "error" in output.lower():

                # Yes an error after a command in AOS6 and in AOS7+

                # Display info message
                log.error(f"set_interface: admin-state: error: {output}")

                # Return an error
                return return_status

        # "description" found?
        if description != None:

            # Yes

            # So description of the interface can be changed

            # Display info message
            log.info("set_interface: description")

            # Adapt the command line

            # 'interfaces <INTERFACE> alias "<DESCRIPTION>"',

            # Replace <INTERFACE> with the interface name
            cmd = self.cmd_set_interface[4].replace("<INTERFACE>", interface)

            # Replace <DESCRIPTION> with the description
            cmd = cmd.replace("<DESCRIPTION>", description)

            # Display info message
            log.info(f"set_interface: description: cmd: {cmd}")

            # Change the description of the interface
            await self.send_command(cmd)

        # "maximum_frame_size" found?
        if maximum_frame_size != None:

            # Yes

            # So the Maximum Frame Size can be changed

            # Display info message
            log.info("set_interface: maximum_frame_size")

            # Adapt the command line

            #  ["interfaces <INTERFACE> max-frame-size <MAXIMUMFRAMESIZE>",
            # "interfaces <INTERFACE> max frame <MAXIMUMFRAMESIZE>",]

            # Replace <INTERFACE> with the interface name
            cmd = self.cmd_set_interface[5].replace("<INTERFACE>", interface)

            # Maximum Frame Size is between 1518-9216

            # Replace <MAXIMUMFRAMESIZE> with the size of the frame
            cmd = cmd.replace("<MAXIMUMFRAMESIZE>", str(maximum_frame_size))

            # Display info message
            log.info(f"set_interface: maximum_frame_size: cmd: {cmd}")

            # Change the Maximum Frame Size of the interface
            output = await self.send_command(cmd)

            # Check if there is an error
            # "                                               ^
            # ERROR: Invalid entry: "max-frame-size""
            if "max-frame-size" in output:

                # The AOS7+ command is not accepted

                # Attempt with AOS6 command

                # Replace <INTERFACE> with the interface name
                cmd = self.cmd_set_interface[6].replace("<INTERFACE>", interface)

                # Replace <MAXIMUMFRAMESIZE> with the size of the frame
                cmd = cmd.replace("<MAXIMUMFRAMESIZE>", str(maximum_frame_size))

                # Change the Maximum Frame Size of the interface
                output = await self.send_command(cmd)

            # Check if there is an error
            # Example:
            # ERROR: Invalid Max Frame Size for non-tagged port/100 (1518-9216): 1234
            #
            #
            if "error" in output.lower():

                # Yes, there is an error

                # Display info message
                log.error(f"set_interface: max-frame-size: error: {output}")

                # Return an error
                return return_status

        # "mode" found?
        if mode != None:

            # Yes

            # So the mode (access, trunk) of the interface can be changed

            # Display info message
            log.info("set_interface: mode")

            # By default, this is Alcatel AOS 7+
            alcatel_version = 7

            # "show vlan members",

            # Get command
            cmd = self.cmd_set_interface[7]

            # Change the mode of the interface
            output = await self.send_command(cmd)

            # Check if an error occured
            #                                          ^
            # ERROR: Invalid entry: "members"
            if "members" in output:

                # Not Alcatel AOS 7+

                # Probably Alcatel AOS 6
                alcatel_version = 6

                # The send a command for Alcatel AOS 6

                # "show vlan port",

                # Get command
                cmd = self.cmd_set_interface[8]

                # Change the mode of the interface
                output = await self.send_command(cmd)

            # Display info message
            log.info(f"set_interface: mode: aos discovered version: {alcatel_version}")

            # Check if there is an error
            if "error" in output.lower():

                # Yes, there is an error

                # Display info message
                log.error(f"set_interface: mode: vlan members: error: {output}")

                # Return an error
                return return_status

            # Let's check if the port is already an access port or a trunk

            # Display info message
            log.info(f"set_interface: mode: checking trunk_type")

            # Convert output into a list of lines
            list_output = output.splitlines()

            # By default the port is an access port
            trunk_type = False

            # By default the list of VLANs is empty for a trunk port
            list_vlan_trunk = []

            # By default the lines read are header
            no_header_data = False

            # Read each line to find data (trunk)
            for line in list_output:

                # Is it the header data without information about VLANS and interfaces?
                if not no_header_data:

                    # Yes

                    # Let's check if it is still the case
                    if line.startswith("---"):

                        # Next time it will be interface data
                        no_header_data = True

                else:

                    # Data after header = interface information

                    # Get "vlan", "port" and "type"
                    vlan_port_type = line.split()

                    # Check if there are 3 values (i.e. "vlan", "port" and "type" in the line)
                    if len(vlan_port_type) >= 3:

                        # Yes, there are 3 values at least

                        # Extract interface name
                        interface_name_possible = vlan_port_type[1]

                        # Check now if the interface name has "/" in the string
                        if "/" in interface_name_possible:

                            # Yes it has

                            # So save the name of the interface
                            interface_name = interface_name_possible

                            # Check if the name of the interface is the same as the one of the line
                            if interface == interface_name:

                                # Yes that is the interface

                                # Extract type (default or qtagged)
                                type_string = vlan_port_type[2]

                                # Check if admin state is "default" or "qtagged"
                                if "qtagged" in type_string:

                                    # type is "trunk"
                                    trunk_type = True

                                    # Get VLAN
                                    vlan_found = vlan_port_type[0]

                                    # Add VLAN to the list of VLANs for a trunk
                                    list_vlan_trunk.append(vlan_found)

                                    # # No need to read more information since we know this is a trunk port

                                    # # Break the loop
                                    # break

            # Display info message
            log.info(
                f"set_interface: mode: trunk_type (False=access, True=trunk): {trunk_type}"
            )

            # Display info message
            log.info(
                f"set_interface: mode: list of VLANs found for a trunk: {list_vlan_trunk}"
            )

            # Check if access port is requested
            if mode == "access":

                # Yes access mode requested for the interface

                # If the interface is already in access mode there is so no need extra configuration

                # Check if the interface is in trunk mode
                if trunk_type:

                    # Yes. The interface is in trunk mode and needs to be changed into access mode

                    # "no vlan <VLAN> members port <INTERFACE>",
                    # "vlan <VLANLIST> no 802.1q <INTERFACE>",

                    # Alcatel AOS 7+?
                    if alcatel_version == 7:

                        # Yes

                        # Replace <INTERFACE> with the interface name
                        cmd_interface_already_filled = self.cmd_set_interface[
                            9
                        ].replace("<INTERFACE>", interface)

                        # Run a command to remove each tagged VLAN of the interface
                        for vlan_8021q in list_vlan_trunk:

                            # Replace <VLAN> with the current VLAN
                            cmd = cmd_interface_already_filled.replace(
                                "<VLAN>", vlan_8021q
                            )

                            # Display info message
                            log.info(
                                f"set_interface: mode: remove tagged vlan: aos 7+: cmd: '{cmd}'"
                            )

                            # Remove all the tagged VLANs on the interface
                            output = await self.send_command(cmd)

                            # Check if there is an error
                            # Example:
                            # ERROR: VPA does not exist
                            #
                            if "error" in output.lower():

                                # Yes, there is an error

                                # Display info message
                                log.error(
                                    f"set_interface: mode: remove tagged vlan: aos 7+: error: {output}"
                                )

                                # Return an error
                                return return_status

                    else:

                        # Alcatel AOS 6

                        # Convert the list of VLANs into a string
                        string_list_vlans = " ".join(list_vlan_trunk)

                        # Replace <INTERFACE> with the interface name
                        cmd = self.cmd_set_interface[10].replace(
                            "<INTERFACE>", interface
                        )

                        # Replace <VLANLIST> with the VLANs
                        cmd = cmd.replace("<VLANLIST>", string_list_vlans)

                        # Display info message
                        log.info(
                            f"set_interface: mode: remove tagged vlan: aos 6: cmd: '{cmd}'"
                        )

                        # Remove all the tagged VLANs on the interface
                        output = await self.send_command(cmd)

                        # Check if there is an error
                        # Example:
                        # ERROR: VLAN 102 does not exist. First create the VLAN
                        #
                        if "error" in output.lower():

                            # Yes, there is an error

                            # Display info message
                            log.error(
                                f"set_interface: mode: remove tagged vlan: aos 6: error: {output}"
                            )

                            # Return an error
                            return return_status

            else:

                # Trunk mode requested for the interface

                # If the interface is already in trunk mode there is so no need extra configuration

                # Check if the interface is in access mode
                if not trunk_type:

                    # Yes. The interface is in access mode and needs to be changed into trunk mode

                    # "show vlan",

                    # Get list of VLANs

                    # Get command
                    cmd = self.cmd_set_interface[11]

                    # Display info message
                    log.info(
                        f"set_interface: mode: add tagged vlan: get list of VLANs: cmd: '{cmd}'"
                    )

                    # Get the list of VLANs
                    output = await self.send_command(cmd)

                    # Convert output into a list of lines
                    list_output = output.splitlines()

                    # By default the list of VLANs is empty
                    list_vlans = []

                    # By default the lines read are header
                    no_header_data = False

                    # Read each line to find data (trunk)
                    for line in list_output:

                        # Is it the header data without information about VLANS?
                        if not no_header_data:

                            # Yes

                            # Let's check if it is still the case
                            if line.startswith("---"):

                                # Next time will be after header
                                no_header_data = True

                        else:

                            # Data after header = VLAN information

                            # Get "vlan"
                            linesplitted = line.split()

                            # Check if there are at least 3 values (i.e. "vlan", "type" and "admin" in the line)
                            if len(linesplitted) >= 3:

                                # Yes, there are at least 3 values

                                # Extract VLAN ID
                                vlan_id = linesplitted[0]

                                # Check if the VLAN ID is a numeric value
                                if vlan_id.isnumeric():

                                    # Yes, it is a number

                                    # Add VLAN to the list of VLANs for a trunk
                                    list_vlans.append(vlan_id)

                    # Display info message
                    log.info(
                        f"set_interface: mode: add tagged vlan: get list of VLANs: list_vlans: {list_vlans}"
                    )

                    # Alcatel AOS 7+?
                    if alcatel_version == 7:

                        # Yes

                        # # Get command
                        # cmd = self.cmd_set_interface[9]

                        # # Change the mode of the interface
                        # output = await self.send_command(cmd)
                        pass

                    else:

                        # Alcatel AOS 6

                        # # Get command
                        # cmd = self.cmd_set_interface[10]

                        # # Change the mode of the interface
                        # output = await self.send_command(cmd)
                        pass

                    pass

                pass

        # No error
        return_status = True

        # Return status
        return return_status
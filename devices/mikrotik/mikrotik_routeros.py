# Python library import
from netscud.base_connection import NetworkDevice, log
import asyncio

# Max data to read in read function
MAX_BUFFER_DATA = 65535


class MikrotikRouterOS(NetworkDevice):
    """
    Class for Mikrotik RouterOS devices
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove useless escape data using the user login
        self.username = self.username + "+cte"

        self._connect_first_ending_prompt = ["> \x1b[K"]
        self.list_of_possible_ending_prompts = [
            "] > ",
        ]
        self._telnet_connect_login = "Login: "
        self._telnet_connect_password = "Password: "
        self._telnet_connect_authentication_fail_prompt = [
            "Login: ",
            "Login failed, incorrect username or password",
        ]

        self._telnet_connect_first_ending_prompt = ["] > "]
        # No global disabling for Mikrotik RouterOS so use
        # "without-paging" at the end of your commands
        self.cmd_disable_paging = None

        self.cmd_exit_config_mode = "/"
        self.cmd_get_version = "system resource print without-paging"
        self.cmd_get_hostname = "system identity print without-paging"
        self.cmd_get_model = "system resource print without-paging"
        self.cmd_get_serial_number = "system routerboard print without-paging"
        self.cmd_get_config = "export"
        self.cmd_get_mac_address_table = "interface bridge host print without-paging"
        self.cmd_get_arp = "ip arp print terse without-paging"
        self.cmd_get_lldp_neighbors = "ip neighbor print terse without-paging"
        # Commands for status, duplex/speed, mode
        self.cmd_get_interfaces = [
            "interface ethernet print terse without-paging",
            "foreach i in=([/interface ethernet find]) do={/interface ethernet monitor $i once without-paging}",
            "interface bridge vlan print terse",
        ]
        self.cmd_get_vlans = "interface bridge vlan print terse without-paging"
        self.cmd_get_routing_table = "ip route print without-paging terse"
        # No command to save the config. So it is always saved after "Enter"
        self.cmd_save_config = ""

    async def connectTelnet(self):
        """
        Async method used for connecting a device using Telnet protocol

        Mikrotik has a special prompt which is difficult to manage. Here
        is an example of the Telnet prompt of Mikrotik switch:

        "\r\r\r\r\r\r[admin@myswitch] >                                                            \r[admin@myswitch] > "

        So this method is special to Mikrotik devices.
        """

        # Display info message
        log.info("connectTelnet")

        try:

            # Prepare connection with Telnet
            conn = asyncio.open_connection(self.ip, self.port)

        except Exception as error:

            # Preparation to the connection failed

            # Display error message
            log.error(f"connectTelnet: preparation to the connection failed: '{error}'")

            # Exception propagation
            raise

        # Display info message
        log.info("connectTelnet: preparation to the connection success")

        try:

            # Connection with Telnet
            self._reader, self._writer = await asyncio.wait_for(
                conn, timeout=self.timeout
            )

        except asyncio.TimeoutError:

            # Time out during connection

            # Display error message
            log.error("connectTelnet: connection: timeout")

            # Exception propagation
            raise

        # Display info message
        log.info("connectTelnet: connection success")

        # Get prompt for the login
        prompt = self._telnet_connect_login

        # Get prompt for the password
        prompt_password = self._telnet_connect_password

        # By default a login is expected
        use_login = True

        # Temporary string variable
        output = ""

        # Temporary bytes variable
        byte_data = b""

        # Read the telnet information and first prompt (for login but a password prompt can be found for IOS for instance)
        while True:

            # Display info message
            log.info(f"connectTelnet: read data for prompt")

            # await asyncio.sleep(2)

            # Read returned prompt
            byte_data += await asyncio.wait_for(
                self._reader.read(MAX_BUFFER_DATA), timeout=self.timeout
            )

            # Display info message
            log.info(f"connectTelnet: byte_data: {byte_data}")

            # Temporary convertion in string. This string has the following form: "b'....'"
            output = str(byte_data)

            # Display info message
            log.info(f"connectTelnet: output: {output}")

            # Prompt for the username found?
            if prompt in output:

                # Yes

                # Leave the loop
                break

            # Prompt for the password found?
            elif prompt_password in output:

                # Yes

                # That means only password is required
                use_login = False

                # Leave the loop
                break

            # A special Telnet string send at first connection?
            elif b"\xff\xfd\x18\xff\xfd \xff\xfd#\xff\xfd" in byte_data:

                # Yes

                # Display info message
                log.info(f"connectTelnet: telnet_init_message")

                # chr(0xFF).chr(0xFB).chr(0x1F).chr(0xFF).chr(0xFB).chr(0x20).chr(0xFF).chr(0xFB).chr(0x18).chr(0xFF).chr(0xFB).chr(0x27).chr(0xFF).chr(0xFD).chr(0x01).chr(0xFF).chr(0xFB).chr(0x03).chr(0xFF).chr(0xFD).chr(0x03).chr(0xFF).chr(0xFC).chr(0x23).chr(0xFF).chr(0xFC).chr(0x24).chr(0xFF).chr(0xFA).chr(0x1F).chr(0x00).chr(0x50).chr(0x00).chr(0x18).chr(0xFF).chr(0xF0).chr(0xFF).chr(0xFA).chr(0x20).chr(0x00).chr(0x33).chr(0x38).chr(0x34).chr(0x30).chr(0x30).chr(0x2C).chr(0x33).chr(0x38).chr(0x34).chr(0x30).chr(0x30).chr(0xFF).chr(0xF0).chr(0xFF).chr(0xFA).chr(0x27).chr(0x00).chr(0xFF).chr(0xF0).chr(0xFF).chr(0xFA).chr(0x18).chr(0x00).chr(0x41).chr(0x4E).chr(0x53).chr(0x49).chr(0xFF).chr(0xF0);
                # Messages in Telnet format
                cmd = b"\xff\xfb\x1f\xff\xfb\x20\xff\xfb\x18\xff\xfb\x27\xff\xfd\x01\xff\xfb\x03\xff\xfd\x03\xff\xfc\x23\xff\xfc\x24\xff\xfa\x1f\x00\x50\x00\x18\xff\xf0\xff\xfa\x20\x00\x33\x38\x34\x30\x30\x2c\x33\x38\x34\x30\x30\xff\xf0\xff\xfa\x27\x00\xff\xf0\xff\xfa\x18\x00\x41\x4e\x53\x49\xff\xf0"

                cmd += b"\xff\xfc\x01\xff\xfc\x22\xff\xfe\x05\xff\xfc\x21"

                # Display info message
                log.info(f"connectTelnet: telnet_init_message: send: {cmd}")

                # Display info message
                log.debug(f"connectTelnet: telnet_init_message: send: '{cmd.hex()}'")

                # Sending command
                self._writer.write(cmd)

                # Temporary bytes variable cleared
                byte_data = b""

        # Display info message
        log.info(f"connectTelnet: login prompt: '{output}'")

        # Login to use?
        if use_login:

            # Yes

            # Display info message
            log.info("connectTelnet: sending login")

            try:

                # Send login
                # await self.send_command(self.username, prompt_password)
                # Sending command
                cmd = self.username + "\r\n"
                self._writer.write(cmd.encode())

                # Display info message
                log.info("connectTelnet: login sent")

            except Exception:

                # Problem with the login

                # Propagate the exception
                raise

        # Display info message
        log.info("connectTelnet: sending password")

        try:
            # Send password
            output = await self.telnet_send_command_with_unexpected_pattern(
                self.password,
                self._telnet_connect_first_ending_prompt,
                self._telnet_connect_authentication_fail_prompt,
            )

        except Exception:

            # Problem with the password

            # Propagate the exception
            raise

        # Display info message
        log.info("connectTelnet: password sent")

    async def send_commandTelnet(self, cmd, pattern=None, timeout=None):
        """
        Async method used to send data to a device

        :param cmd: command to send
        :type cmd: str

        :param pattern: optional, a pattern replacing the prompt when the prompt is not expected
        :type pattern: str

        :param timeout: optional, a timeout for the command sent. Default value is self.timeout
        :type timeout: str

        :return: the output of command
        :rtype: str
        """

        # Debug info message
        log.info("send_commandTelnet")

        # Default value of timeout variable
        if timeout is None:
            timeout = self.timeout

        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\r\n"

        # Sending command
        self._writer.write(cmd.encode())

        # Temporary string variable
        output = ""

        # Temporary bytes variable
        byte_data = b""

        # Variable used for leaving loop (necessary sonce there is a "while" with a "for" and a "break" command)
        stay_in_loop = True

        try:

            # Read data
            while stay_in_loop:

                # Read returned prompt
                byte_data += await asyncio.wait_for(
                    self._reader.read(MAX_BUFFER_DATA), timeout=timeout
                )

                # Display info message
                log.info(f"send_commandTelnet: byte_data: '{byte_data}'")

                # Temporary convertion in string. This string has the following form: "b'....'"
                output = str(byte_data)

                # Display info message
                log.info(f"send_commandTelnet: output: '{output}'")

                # Is a patten used?
                if pattern:

                    # Use pattern instead of prompt
                    if pattern in output:

                        # Yes

                        # Leave the loop
                        break

                else:

                    # Check if prompt is found
                    for prompt in self.list_of_possible_ending_prompts:

                        # A pattern found twice (or more)?
                        if output.count(prompt) >= 2:

                            # Yes

                            # Display info message
                            log.info(
                                f"send_commandTelnet: prompt found twice or more: '{prompt}'"
                            )

                            # Will leave the while loop
                            stay_in_loop = False

                            # Leave the loop
                            break

        except asyncio.TimeoutError:

            # Time out during when reading prompt

            # Display error message
            log.error("send_commandTelnet: connection: timeout")

            # Exception propagation
            raise

        except Exception as error:

            # Error during when reading prompt

            # Display error message
            log.error(f"send_commandTelnet: error: {error}")

            # Exception propagation
            raise

        # Convert data (bytes) into string
        output = byte_data.decode("utf-8", "ignore")

        # Debug info message
        log.info(
            f"send_commandTelnet: raw output: '{output}'\nsend_commandTelnet: raw output (hex): '{output.encode().hex()}'"
        )

        # Remove the command sent from the result of the command
        # output = self.remove_command_in_output(output, str(cmd))
        # For Mikrotik just remove the first line (complicated otherwise)
        output = output.split("\n\r", 1)[1]
        # Remove the carriage return of the output
        # output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        # For Mikrotik just remove the last line (complicated otherwise)
        output = output[: output.rfind("\n")] + "\n"

        # Debug info message
        log.info(
            f"send_commandTelnet: cleaned output: '{output}'\nsend_commandTelnet: cleaned output (hex): '{output.encode().hex()}'"
        )

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)

        # Return the result of the command
        return output

    async def telnet_send_command_with_unexpected_pattern(
        self, cmd, pattern, error_pattern=None, timeout=None
    ):
        """
        Async method used to send command for Telnet connection to a device with possible unexpected patterns

        send_command can wait till time out if login and password are wrong. This method
        speed up the returned error message when authentication failed is identified.
        This method is limited to authentication whem password is required

        :param cmd: command to send
        :type cmd: str

        :param pattern: optional, a list of patterns located at the very end of the a returned string. Can be used
            to define a custom or unexpected prompt a the end of a string
        :type pattern: str

        :param timeout: optional, a timeout for the command sent. Default value is self.timeout
        :type timeout: str

        :param error_pattern: optional, a list of failed prompts found when the login and password are not correct
        :type error_pattern: str

        :return: the output of command
        :rtype: str
        """

        # Debug info message
        log.info("telnet_send_command_with_unexpected_pattern")

        # Default value of timeout variable
        if timeout is None:
            timeout = self.timeout

        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        # Sending command
        self._writer.write(cmd.encode())

        # Temporary string variable
        output = ""

        # Temporary bytes variable
        byte_data = b""

        # By default pattern is not found
        pattern_not_found = True

        try:

            # Read data
            while pattern_not_found:

                # Read returned prompt
                byte_data += await asyncio.wait_for(
                    self._reader.read(MAX_BUFFER_DATA), timeout=timeout
                )

                # Display info message
                log.info(
                    f"telnet_send_command_with_unexpected_pattern: byte_data: '{byte_data}'"
                )

                # Display debug message
                log.debug(
                    f"telnet_send_command_with_unexpected_pattern: byte_data: hex: '{byte_data.hex()}'"
                )

                # Temporary convertion in string. This string has the following form: "b'....'"
                output = str(byte_data)

                # Display info message
                log.info(
                    f"telnet_send_command_with_unexpected_pattern: output: '{output}'"
                )

                # Is a pattern used?
                if pattern:

                    # Check all pattern of prompt in the output
                    for prompt in pattern:

                        # Display info message
                        log.info(
                            f"telnet_send_command_with_unexpected_pattern: checking prompt: '{prompt}'"
                        )

                        # A pattern found twice (or more)?
                        if output.count(prompt) >= 2:
                            # if prompt in output:

                            # Yes

                            # A pattern is found. The main loop can be stopped
                            pattern_not_found = False

                            # Display info message
                            log.info(
                                f"telnet_send_command_with_unexpected_pattern: prompt found: '{prompt}'"
                            )

                            # Leave the loop
                            break

                # Is an unexpected pattern used?
                if error_pattern and pattern_not_found:

                    # Check all unexpected pattern of prompt in the output
                    for bad_prompt in error_pattern:

                        # Display info message
                        log.info(
                            f"telnet_send_command_with_unexpected_pattern: checking unexpected prompt: '{bad_prompt}'"
                        )

                        # An error_pattern pattern found?
                        if bad_prompt in output:

                            # Yes

                            # Display error message
                            log.error(
                                "telnet_send_command_with_unexpected_pattern: authentication failed"
                            )

                            # Raise exception
                            raise Exception(
                                "telnet_send_command_with_unexpected_pattern: authentication failed"
                            )

                            # Leave the loop
                            # break

        except asyncio.TimeoutError:

            # Time out during when reading prompt

            # Close the connection in order to not display RuntimeError
            await self.disconnect()

            # Display error message
            log.error(
                "telnet_send_command_with_unexpected_pattern: reading prompt: timeout"
            )

            # Exception propagation
            raise

        except Exception as error:

            # Error during when reading prompt

            # Close the connection in order to not display RuntimeError
            await self.disconnect()

            # Display error message
            log.error(
                f"telnet_send_command_with_unexpected_pattern: reading prompt: error: {error}"
            )

            # Exception propagation
            raise

        # Convert data (bytes) into string
        output = byte_data.decode("utf-8", "ignore")

        # Debug info message
        log.info(
            f"telnet_send_command_with_unexpected_pattern: raw output: '{output}'\ntelnet_send_command_with_unexpected_pattern: raw output (hex): '{output.encode().hex()}'"
        )

        # Remove the command sent from the result of the command
        # output = self.remove_command_in_output(output, str(cmd))
        output = output.split("\n\r", 1)[1]
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        # For Mikrotik just remove the last line (complicated otherwise)
        output = output[: output.rfind("\n")] + "\n"

        # Debug info message
        log.info(
            f"telnet_send_command_with_unexpected_pattern: cleaned output: '{output}'\ntelnet_send_command_with_unexpected_pattern: cleaned output (hex): '{output.encode().hex()}'"
        )

        # Return the result of the command
        return output

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

        :return: MAC address table of the device
        :rtype: list of dict
        """

        # Display info message
        log.info("get_mac_address_table")

        # By default nothing is returned
        returned_output = []

        # Send a command
        output = await self.send_command(self.cmd_get_mac_address_table)

        # Convert string to list of string and remove the 2 first lines
        lines = output.splitlines()[2:]

        # Read each line
        for line in lines:

            # Set default values for variables
            mac_type = None
            mac_address = None
            vlan = None
            interface = None

            # If the MAC address is dynamic AND local then it is self (its own MAC address)

            # Get the type of MAC address (dynamic, static or self)
            if len(line) > 6:

                if line[6].lower() == "l":

                    # Self MAC address
                    mac_type = "self"

                # Get the type of MAC address (dynamic, static or self)
                elif line[5].lower() == "d":

                    # Dynamic MAC address
                    mac_type = "dynamic"
                else:

                    # Static MAC address
                    mac_type = "static"

            # Get MAC address
            if len(line) > 26:
                mac_address = line[9:26]

            # Get VLAN
            if len(line) > 31:
                vlan = line[27:31].strip()

            # Get interface
            if len(line) > 32:
                interface = line[32:].split()[0]

            # Create a dictionary
            mac_dict = {
                "mac_type": mac_type,
                "mac_address": mac_address,
                "vlan": vlan,
                "interface": interface,
            }

            # Add the MAC information to the list
            if mac_address:
                returned_output.append(mac_dict)

        # Return data
        return returned_output

    async def get_arp_table(self):
        """
        Asyn method used to get the ARP table of the device

        :return: ARP table of the device
        :rtype: list of dict
        """

        # Display info message
        log.info("get_arp_table")

        # By default nothing is returned
        returned_output = []

        # Send a command
        output = await self.send_command(self.cmd_get_arp)

        # Display info message
        log.info(f"get_arp:\n'{output}'")

        # Convert a string into a list of strings
        lines = output.splitlines()

        # Read each line
        for line in lines:

            # Set default values for variables
            address = None
            mac_address = None
            interface = None

            # Get IP address
            if " address=" in line:
                address = line.split(" address=")[-1].split()[0]

            # Get MAC address
            if " mac-address=" in line:
                mac_address = line.split(" mac-address=")[-1].split()[0]

            # Get interface
            if " interface=" in line:
                interface = line.split(" interface=")[-1].split()[0]

            # Create a dictionary
            returned_dict = {
                "address": address,
                "mac_address": mac_address,
                "interface": interface,
            }

            # Add the information to the list
            if address:
                returned_output.append(returned_dict)

        # Return data
        return returned_output

    async def get_lldp_neighbors(self):
        """
        Asyn method used to get the LLDP information from the device

        The problem with LLDP implementation on RouterOS is that the command
        used to get LLDP information can return data even though there is no
        LLDP service running on neighbour device. Thus Interface and MAC
        addresses fields could be filled of data without LLDP neighbour
        device. Data will be considered as LLDP information is there are
        other fields than Interface and MAC addresses are found.

        :return: LLDP information of the device
        :rtype: dict of list of dict
        """

        # Display info message
        log.info("get_lldp_neighbors")

        # By default nothing is returned
        returned_output = {}

        # Send a command
        output = await self.send_command(self.cmd_get_lldp_neighbors)

        # Display info message
        log.info(f"get_lldp_neighbors:\n'{output}'")

        # Convert a string into a list of strings
        lines = output.splitlines()

        # Read each line
        for line in lines:

            # Default value for local interface (no interface)
            local_interface = None

            # Initialize potential LLDP data with default values
            chassis_id = ""
            port_id = ""
            ttl = None
            port_description = ""
            system_name = ""
            system_description = ""
            system_capabilities = []
            management_address = ""

            # Get local interface
            if " interface=" in line:
                local_interface = line.split(" interface=")[-1].split()[0].split(",")[0]

                # Display info message
                log.info(f"get_lldp_neighbors: local_interface: {local_interface}")

            # Get Chassis ID - TLV type 1
            if " mac-address=" in line:
                chassis_id = line.split(" mac-address=")[-1].split()[0]

                # Display info message
                log.info(f"get_lldp_neighbors: chassis_id: {chassis_id}")

            # Get Port ID - TLV type 2
            if " interface-name=" in line:
                port_id = (
                    line.split(" interface-name=")[-1].split("=")[0].rsplit(" ", 1)[0]
                )

                # Display info message
                log.info(f"get_lldp_neighbors: port_id: {port_id}")

            # Get Time To Live - TLV type 3
            # Not available on RouterOS. "age" parameter is a decreasing counter

            # Get Port description - TLV type 4
            # Not available on RouterOS.

            # Get System name - TLV type 5
            if " identity=" in line:
                system_name = line.split(" identity=")[-1].split()[0]

                # Check if return value is a string "" (just double quotes which means empty data)
                if system_name == '""':

                    # Yes, empty string
                    system_name = ""

                # Display info message
                log.info(f"get_lldp_neighbors: system_name: {system_name}")

            # Get System description - TLV type 6
            if " system-description=" in line:
                system_description = (
                    line.split(" system-description=")[-1]
                    .split("=")[0]
                    .rsplit(" ", 1)[0]
                )

                # Display info message
                log.info(
                    f"get_lldp_neighbors: system_description: {system_description}"
                )

            # Get System capabilities - TLV type 7
            if " system-caps=" in line:

                # First get the capablities as a string separated by commas
                # e.g.: 'bridge,wlan-ap,router,station-only'
                string_capability = line.split(" system-caps=")[-1].split()[0]

                # Then convert them into a list of characters
                # Code	Capability
                # B	    Bridge (Switch)
                # C	    DOCSIS Cable Device
                # O	    Other
                # P	    Repeater
                # R	    Router
                # S	    Station
                # T	    Telephone
                # W	    WLAN Access Point

                # Read each capability
                for capability in string_capability.split(","):

                    # Check if string is not null
                    if len(capability) > 0:

                        # Get the first letter of the capability, convert this character in uppercase
                        # and add it to a list
                        system_capabilities.append(capability[0].upper())

                # Display info message
                log.info(
                    f"get_lldp_neighbors: system_capabilities: {system_capabilities}"
                )

            # Get Management address - TLV type 8
            if " address=" in line:
                management_address = line.split(" address=")[-1].split()[0]

            # LLDP TLV Type 9 to 127 are currently not supported by this method

            # Check if data can be considered as LLDP
            if local_interface and (
                port_id or system_name or system_description or management_address
            ):

                # Probably LLDP

                # Create a dictionary
                returned_dict = {
                    "chassis_id": chassis_id,
                    "port_id": port_id,
                    "ttl": ttl,
                    "port_description": port_description,
                    "system_name": system_name,
                    "system_description": system_description,
                    "system_capabilities": system_capabilities,
                    "management_address": management_address,
                }

                # Add the information to the dict
                returned_output[local_interface] = returned_output.get(
                    local_interface, []
                ) + [returned_dict]

        # Return data
        return returned_output

    async def get_interfaces(self):
        """
        Asyn method used to get the interfaces information from the device

        some commands are used to collect interface data:
        - one for status
        - one for duplex/speed
        - one for mode (access / trunk)

        :return: Interfaces of the device
        :rtype: dict of dict
        """

        # Display info message
        log.info("get_interfaces")

        # By default nothing is returned
        returned_output = {}

        # Command for the status of the interfaces

        # Send a command
        output_status = await self.send_command(self.cmd_get_interfaces[0])

        # Display info message
        log.info(f"get_interfaces: status command\n'{output_status}'")

        # Command for the speed and the duplex mode of the interfaces

        # Send a command
        output_bitrate = await self.send_command(self.cmd_get_interfaces[1])

        # Display info message
        log.info(f"get_interfaces: speed duplex command\n'{output_bitrate}'")

        # Command for the mode of the interfaces (access or trunk)

        # Send a command
        output_mode = await self.send_command(self.cmd_get_interfaces[2])

        # Display info message
        log.info(f"get_interfaces: mode command\n'{output_mode}'")

        # Convert a string into a list of strings (status)
        lines = output_status.splitlines()

        # Convert a string into a list of block of strings (duplex/speed)
        block_of_strings_bitrate = output_bitrate.split("\n\n")

        # Convert a string into a list of block of strings (mode)
        block_of_strings_mode = output_mode.splitlines()

        # By default there is no trunk interface
        dict_trunk_interface = {}

        # Read all tagged interfaces line by line
        for line in block_of_strings_mode:

            # Check if a " tagged=" is inside the string
            if " tagged=" in line:

                # Yes

                # Save the string with the name of the interfaces separated with a comma
                tagged_interfaces = line.split(" tagged=")[-1].split()[0]

                # Check if value is not empty
                if tagged_interfaces != '""':

                    # Not empty

                    # Read all trunk interfaces found and separate them
                    for interface_trunk in tagged_interfaces.split(","):

                        # Save the trunk interface
                        dict_trunk_interface[interface_trunk] = True

        # Read each line
        for line in lines:

            # Initialize data with default values
            interface_name = ""
            operational = False
            admin_state = False
            maximum_frame_size = 0
            full_duplex = False
            speed = 0  # speed is in Mbit/s
            mode = "access"
            description = ""

            # Get interface name
            if " name=" in line:
                interface_name = line.split(" name=")[-1].split()[0]

                # Display info message
                log.info(f"get_interfaces: interface_name: {interface_name}")

                # Get operational and admin_state status
                if len(line) > 3:
                    data = line[3].upper()

                    # operational + admin_state = "up"?
                    if data == "R":

                        # Yes
                        operational = True
                        admin_state = True

                    # operational = "down" and admin_state = "up"?
                    elif data == " ":

                        # Yes
                        admin_state = True

                    # operational + admin_state = "down" means data == "X"
                    # No need to compare since default values are already fine

                # Display info message
                log.info(f"get_interfaces: operational: {operational}, admin_state")

                # Get maximum frame size
                if " l2mtu=" in line:
                    maximum_frame_size = int(line.split(" l2mtu=")[-1].split()[0])

                    # Display info message
                    log.info(
                        f"get_interfaces: maximum_frame_size : {maximum_frame_size}"
                    )

                # Get speed and duplex information

                for index, data_block in enumerate(block_of_strings_bitrate):

                    # Display info message
                    log.info(
                        f"get_interfaces: get_speed: index: {index} [{len(block_of_strings_bitrate)}]"
                    )

                    # Is the name of interface found in the block of strings?
                    if f"name: {interface_name}" in data_block:

                        # Yes, so this block of strings has information on the interface

                        # Display info message
                        log.info(f"get_interfaces: get_speed: index found: {index}")

                        # " rate: " field found in the block of strings? (speed)
                        if " rate: " in data_block:

                            # Yes

                            # Then extract the string data
                            rate_string = (
                                data_block.split(" rate: ")[-1].split()[0].lower()
                            )

                            # Is is mbps?
                            if "mbps" in rate_string:
                                # Yes

                                # Then speed is saved
                                speed = int(float(rate_string.split("mbps")[0]))

                            # Is is gbps?
                            elif "gbps" in rate_string:

                                # Yes

                                # Then speed is saved in mpbs
                                speed = int(float(rate_string.split("gbps")[0]) * 1000)

                            # Is is tbps? (not seen on current Mikrotik product; for future use)
                            elif "tbps" in rate_string:
                                # Yes

                                # Then speed is saved in mpbs
                                speed = int(
                                    float(rate_string.split("tbps")[0]) * 1000000
                                )

                            # Display info message
                            log.info(
                                f"get_interfaces: get_speed: rate found: {rate_string}, rate: {speed} mbps"
                            )

                        # " full-duplex: yes" field found in the block of strings? (full_duplex)
                        if " full-duplex: yes" in data_block:

                            # Yes

                            # Display info message
                            log.info(
                                f"get_interfaces: get_duplex: {interface_name} is in full duplex mode"
                            )

                            # Then the insterface is in full duplex mode
                            full_duplex = True

                        # Remove current interface information from the block of data
                        # (to speed up the research of data)
                        del block_of_strings_bitrate[index]

                        # Leave the loop
                        break

                # Get interface mode (access or trunk)

                # Check if the interface is one of the trunk interface
                if interface_name in dict_trunk_interface:

                    # Yes

                    # Set trunk mode
                    mode = "trunk"

                    # Display info message
                    log.info(f"get_interfaces: mode: {mode}")

                # # Get input erros, FCS errors, input packets anf output packets
                # for index, data_stats in enumerate(block_of_strings_stats):

                #     # Display info message
                #     log.info(
                #         f"get_interfaces: get_stats: index: {index} [{len(block_of_strings_stats)}]"
                #     )

                #     # Is the name of interface found in the block of strings?
                #     if f"name: {interface_name}" in data_stats:

                #         # Yes, so this block of strings has information on the interface

                #         # Display info message
                #         log.info(f"get_interfaces: get_stats: index found: {index}")

                #         # " rx-fcs-error=" filed found in the block of strings? (speed)
                #         if " rx-fcs-error=" in data_stats:

                #             # Yes

                #             # Save the line with the data of FCS errors
                #             line_split = data_stats.split("rx-fcs-error=")[-1].split("=")[0]

                #             # By default no string gathered
                #             fcs_string = ""

                #             # Check each character till a non-numeric character
                #             for character in line_split:

                #                 # Display info message
                #                 log.info(
                #                     f"get_interfaces: get_stats: fcs errors: char = {character}"
                #                 )

                #                 # Is it a numeric characer ("0" to "9")?
                #                 if character >= "0" and character <= "9":

                #                     # Yes

                #                     # So the character is added to a string
                #                     fcs_string += character

                #                 # Is the character different than " " (which can be used for separator)?
                #                 elif character != " ":

                #                     # Yes, this is not a space

                #                     # Leave the loop then since this is the beginning of another word
                #                     break

                #             log.info(
                #                 f"get_interfaces: get_stats: fcs errors: fcs_string: {fcs_string}"
                #             )

                #             # String not empty?
                #             if fcs_string:

                #                 # Yes

                #                 # Then save the result in integer
                #                 fcs_error = int(fcs_string)

                # Get description
                if " comment=" in line:
                    description = (
                        line.split(" comment=")[-1].split("=")[0].rsplit(" ", 1)[0]
                    )

                    # Display info message
                    log.info(f"get_interfaces: comment: {description}")

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

    async def get_vlans(self):
        """
        Asyn method used to get the vlans information from the device

        :return: VLANs of the device
        :rtype: dict
        """

        # Display info message
        log.info("get_vlans")

        # By default nothing is returned
        returned_output = {}

        # Send a command
        output = await self.send_command(self.cmd_get_vlans)

        # Display info message
        log.info(f"get_vlans:\n'{output}'")

        # Convert a string into a list of strings
        lines = output.splitlines()

        # Read each line
        for line in lines:

            # Initialize data with default values
            name = ""
            vlan_id = 0
            extra = None
            # extra = {
            #     "bridge": "",
            # }

            # Get VLAN name
            if " comment=" in line:
                name = line.split(" comment=")[-1].split("=")[0].rsplit(" ", 1)[0]

                # Display info message
                log.info(f"get_vlans: name: {name}")

            # Get VLAN ID
            if " vlan-ids=" in line:
                vlan_id = int(line.split(" vlan-ids=")[-1].split()[0])

                # Display info message
                log.info(f"get_vlans: vlan_id: {vlan_id}")

            # Get bridge (special Mikrotik)
            if " bridge=" in line:
                bridge = line.split(" bridge=")[-1].split("=")[0].rsplit(" ", 1)[0]

                # Display info message
                log.info(f"get_vlans: bridge: {bridge}")

                # Save bridge information into
                extra = {
                    "bridge": bridge,
                }

            # Create a dictionary
            returned_dict = {
                "name": name,
                "extra": extra,
            }

            # Is VLAN ID not nul?
            if vlan_id:

                # Yes

                # Add the information to the dict
                returned_output[vlan_id] = returned_dict

        # Return data
        return returned_output

    async def get_routing_table(self):
        """
        Asyn method used to get the routing table of the device

        :return: Routing table of the device
        :rtype: dict
        """

        # Display info message
        log.info("get_routing_table")

        # By default nothing is returned
        returned_output = {}

        # Send a command
        output = await self.send_command(self.cmd_get_routing_table)

        # Display info message
        log.info(f"get_routing_table:\n'{output}'")

        # Convert a string into a list of strings
        lines = output.splitlines()

        # Read each line
        for line in lines:

            # Initialize data with default values
            network = ""
            address = ""
            prefix = 0
            protocol = "unknown"
            administrative_distance = 0
            gateway = ""
            active = False
            protocol_attributes = None

            # Get network, address and prefix
            if " dst-address=" in line:
                network = line.split(" dst-address=")[-1].split()[0]
                address = network.split("/")[0]
                prefix = int(network.split("/")[1])

            # Get protocol

            # Save char with protocol letter
            if len(line) > 5:

                protocol_char = line[5]

                if protocol_char == "C":

                    # Connected
                    protocol = "connected"

                elif protocol_char == "S":

                    # Static
                    protocol = "static"

                elif protocol_char == "r":

                    # RIP
                    protocol = "rip"

                elif protocol_char == "b":

                    # BGP
                    protocol = "bgp"

                elif protocol_char == "o":

                    # OSPF
                    protocol = "ospf"

                elif protocol_char == "m":

                    # MME
                    protocol = "mme"

            # Get administrative distance
            if " distance=" in line:
                administrative_distance = int(line.split(" distance=")[-1].split()[0])

            # Get gateway
            if " gateway=" in line:
                gateway = line.split(" gateway=")[-1].split()[0]

            # Get active status
            if len(line) > 3:

                if line[3] == "A":
                    active = True

            # Create a dictionary
            returned_dict = {
                "address": address,
                "prefix": prefix,
                "protocol": protocol,
                "administrative_distance": administrative_distance,
                "gateway": gateway,
                "active": active,
                "protocol_attributes": protocol_attributes,
            }

            # Is a network found?
            if network:

                # Yes

                # Add the information to the dict
                returned_output[network] = returned_dict

        # Return data
        return returned_output

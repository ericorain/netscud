# Python library import
import asyncio, asyncssh, logging

# Module logging logger
log = logging.getLogger(__package__)

# Debug level
#logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.INFO)
#asyncssh.set_debug_level(1)


# Declaration of constant values

# Max data to read in read function
MAX_BUFFER_DATA = 65535


class NetworkDevice:
    """
    Base class for network object


    :param ip: IP address of a device
    :type ip: str

    :param username: Username used to connect to a device
    :type username: str

    :param password: Password used to connect to a device
    :type password: str

    :param device_type: Type of device used
    :type device_type: str

    :param port: TCP port used to connect a device. Default value is "22" for SSH
    :type port: int, optional

    :param timeout: TCP port used to connect a device. Default value is 10 seconds
    :type timeout: int, optional

    :param _protocol: Protocol used to connect a device. "ssh" or "telnet" are possible options. Default value is "ssh"
    :type _protocol: str, optional

    :param enable_mode: Enable mode for devices requiring it. Default value is "False"
    :type enable_mode: bool, optional

    :param enable_password: Enable password used for enable mode.
    :type enable_password: str, optional

    :param conn: Variable used for the management of the SSH connection
    :type conn: SSHClientConnection object

    :param _writer: Variable used for the management of the Telnet connection and writing channel
    :type _writer: StreamWriter object

    :param _reader: Variable used for the management of the Telnet reading channel
    :type _reader: StreamReader object

    :param possible_prompts: Used by the connect method to list all possible prompts of the device
    :type possible_prompts: list

    :param _connect_first_ending_prompt: Default possible ending prompts. Used only the time after login and password to discover the prompt
    :type _connect_first_ending_prompt: list
    
    :param list_of_possible_ending_prompts: Different strings at the end of a prompt the device can get. Used for detecting the prompt returned in sent commands
    :type list_of_possible_ending_prompts: list

    :param _telnet_connect_login: Login prompt for Telnet. Used to detect when a login is expected or when login and password access is failed
    :type _telnet_connect_login: str

    :param _telnet_connect_password: Password prompt for Telnet. Used to detect when a login is expected or when login and password access is failed
    :type _telnet_connect_password: list

    :param _telnet_connect_authentication_fail_prompt: Known failing messages or prompts when an authentication has failed. Used to get an answer faster than timeout events
    :type _telnet_connect_authentication_fail_prompt: list

    :param cmd_enable: Enable command for entering into enable mode
    :type cmd_enable: str

    :param cmd_disable_paging: Command used to disable paging on a device. That command is run at connection time
    :type cmd_disable_paging: str

    :param cmd_enter_config_mode: Command used to enter into a configuration mode on a device when this device support that feature.
    :type cmd_enter_config_mode: str

    :param cmd_exit_config_mode: Command used to leave a configuration mode on a device when this device support that feature.
    :type cmd_exit_config_mode: str

    :param cmd_get_version: API command used to get the software version of a device
    :type cmd_get_version: str

    :param cmd_get_hostname: API command used to get the hostname of a device
    :type cmd_get_hostname: str

    :param cmd_get_model: API command used to get the model of a device
    :type cmd_get_model: str

    :param cmd_get_serial_number: API command used to get the serial number of a device
    :type cmd_get_serial_number: str

    :param cmd_get_config: API command used to get the running configuration of a device
    :type cmd_get_config: str

    :param cmd_save_config: API command used to save the running configuration on the device
    :type cmd_save_config: str
    """

    def __init__(self, **kwargs):

        # Display info message
        log.info("__init__")

        self.ip = ""
        self.username = ""
        self.password = ""
        self.device_type = ""
        self.port = 22
        self.timeout = 10
        self._protocol = "ssh"
        self.enable_mode = False
        self.enable_password = ""
        self.conn = None
        self._writer = None
        self._reader = None
        self.possible_prompts = []
        self._connect_first_ending_prompt = ["#",">"]
        self.list_of_possible_ending_prompts = [
            "(config-line)#",
            "(config-if)#",
            "(config)#",
            ">",
            "#",
        ]
        self._send_command_error_in_returned_output = []
        self._telnet_connect_login = "Username:"
        self._telnet_connect_password = "Password:"
        self._telnet_connect_authentication_fail_prompt = [":","%"]
        self.cmd_enable = "enable"
        self.cmd_disable_paging = "terminal length 0"
        self.cmd_enter_config_mode = "configure terminal"
        self.cmd_exit_config_mode = "exit"
        self.cmd_get_version = "show version"
        self.cmd_get_hostname = "show version | include uptime"
        self.cmd_get_model = "show inventory"
        self.cmd_get_serial_number = "show inventory | i SN"
        self.cmd_get_config = "show running-config"
        self.cmd_save_config = "write memory"
        

        # Display info message
        log.info("__init__: kwargs: " + str(kwargs))


        # Get information from dictionary

        # "ip" found?
        if 'ip' in kwargs:
            
            # Save "ip" parameter
            self.ip = kwargs['ip']
            
            # Display info message
            log.info("__init__: ip found: " + str(self.ip))

        # "username" found?
        if 'username' in kwargs:
            self.username = kwargs['username']

            # Display info message
            log.info("__init__: username found: " + str(self.username))
        
        # "password" found?
        if 'password' in kwargs:
            self.password = kwargs['password']

            # Display info message
            log.info("__init__: password found: " + str(self.password))

        # "device_type" found?
        if 'device_type' in kwargs:
            self.device_type = kwargs['device_type']
            
            # Display info message
            log.info("__init__: device_type found: " + str(self.device_type))

        # "timeout" found?
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']

            # Display info message
            log.info("__init__: timeout found: " + str(self.timeout))

        # "protocol" found?
        if 'protocol' in kwargs:
            self._protocol = kwargs['protocol'].lower()

            # Display info message
            log.info("__init__: protocol found: " + str(self._protocol))
            
            # By default telnet port is 23
            if self._protocol.lower() == "telnet":
                self.port = 23
        
        # "port" found?
        if 'port' in kwargs:
            self.port = kwargs['port']

            # Display info message
            log.info("__init__: port found: " + str(self.port))

        # "enable_mode" found?
        if 'enable_mode' in kwargs:
            self.enable_mode = kwargs['enable_mode']

            # Display info message
            log.info("__init__: enable_mode found: " + str(self.enable_mode))

        # "enable_password" found?
        if 'enable_password' in kwargs:
            self.enable_password = kwargs['enable_password']

            # Display info message
            log.info("__init__: enable_password found: " + str(self.enable_password))




    def find_prompt(self, text):
        """
        Method used to find a prompt inside an output string

        This method is used during the first communication with the device.
        First it find the prompt then caculate the different forms the prompt
        can take. This will be useful later on while finding prompt in other
        output stream (read).

        :param text: data with a prompt
        :type text: str

        :return: the prompt found
        :rtype: str
        """

        # Get last line of the data
        prompt = text.split('\n')[-1]

        # Display info message
        log.info("find_prompt: prompt: '" + str(prompt) + "'")

        # Get the possible prompts for future recognition
        self.possible_prompts = self.get_possible_prompts(prompt)

        # Return the prompt
        return prompt

    def get_possible_prompts(self, prompt):
        """
        Method used to check if a prompt has one of the expected endings then
        create a list with all possible prompts for the device

        :param prompt: a prompt with a possible ending prompt (eg. "switch#")
        :type prompt: str

        :return: the list of prompts
        :rtype: list
        """

        # By default no prompts are returned
        list_of_prompts = []

        # Get all the ppossible values of the endings of the prompt
        list_of_possible_ending_prompts = self.list_of_possible_ending_prompts

        # Temporary variable storing the prompt value
        my_prompt = prompt

        # Test each possible prompt ending (i.e '#', '>', "(config-if)#", "(config)#")
        for ending in list_of_possible_ending_prompts:

            # Is this current prompt ending at the end of the prompt?
            if my_prompt.endswith(ending):

                # Yes

                # Then remove the ending
                my_prompt = my_prompt[:-len(ending)]

                # Break the loop
                break


        # Prompt should be from "switch#" to "switch"

        # Display info message
        log.info("get_possible_prompts: prompt found: '" + my_prompt + "'")

        # Now create all the possible prompts for that device
        for ending in list_of_possible_ending_prompts:

            # Save the prompt name with a possible ending in the list
            list_of_prompts.append(my_prompt + ending)

        # Display info message
        log.info("get_possible_prompts: list of possible prompts: " + str(list_of_prompts))

        # Return the list of prompts
        return list_of_prompts


    def check_if_prompt_is_found(self, text):
        """
        Method used to check if a prompt is detected inside a string        

        :param text: a string with prompt
        :type text: str

        :return: the prompt found
        :rtype: str
        """

        # By default the prompt is not found
        prompt_found = False

        # Check all possible prompts
        for prompt in self.possible_prompts:

            # Display info message
            log.info("check_if_prompt_is_found: prompt: '" + str(prompt) + "'")

            # Is this prompt present in the text?
            if prompt in text:

                # Yes
                prompt_found = True

                # Display info message
                log.info("check_if_prompt_is_found: prompt found: '" + str(prompt) + "'")

                # Leave the for loop
                break
        
        # Return the prompt found
        return prompt_found



    def remove_command_in_output(self, text, cmd):
        """
        Method removing the command at the beginning of a string

        After sending commands an "echo" of the command sent
        is display in the output string. This method removes it.

        :param text: the text with the command at the beginning
        :type text: str

        :param cmd: the command previously sent
        :type cmd: str

        :return: the output string without the command
        :rtype: str
        """

        # Display info message
        log.info("remove_command_in_output: cmd = '" + str(cmd) + "'")
        
        # Display info message
        log.info("remove_command_in_output: cmd (hex) = '" + cmd.encode().hex() + "'")
        
        # Remove the command from the beginning of the output
        output = text.lstrip(cmd)

        # Return the string without the command
        return output

    def remove_starting_carriage_return_in_output(self, text):

        """
        Method removing the carriage return at the beginning of a string

        :param text: the text with the command at the beginning
        :type text: str

        :return: the output string without the starting carriage return
        :rtype: str
        """

        # Display info message
        log.info("remove_starting_carriage_return_in_output")

        # Remove the carriage return at the beginning of the string
        output = text.lstrip("\r\n\r")

        # Return the string without the starting carriage return
        return output

    def remove_ending_prompt_in_output(self, text):
    
        """
        Method removing the prompt at the end of a string

        :param text: the text with a prompt at the beginning
        :type text: str

        :return: the output string without the ending prompt
        :rtype: str
        """

        # Display info message
        log.info("remove_ending_prompt_in_output")

        # Check all possible prompts
        for prompt in self.possible_prompts:

            # Display info message
            log.info("remove_ending_prompt_in_output: prompt: '" + str(prompt) + "'")

            # Prompt found in the text?
            if prompt in text:

                # Yes

                # Then it is removed from the text
                text = text.rstrip(prompt)

                # Remove also carriage return
                text = text.rstrip("\r\n")

                # Leave the loop
                break

        #output = text.rstrip("\r\n" + self.prompt)

        # Display info message
        log.info("remove_ending_prompt_in_output: text without prompt:\n'" + text + "'")

        # Return the text without prompt at the end
        return text


    def check_error_output(self, output):
        """
        Check if an error is returned by the device ("% Unrecognized command", "% Ambiguous command", etc.)

        If an error is found, then an exception is raised
        """

        # Display info message
        log.info("check_error_output")

        # Check if output has some data
        if output:

            # Yes

            # Display info message
            log.info("check_error_output: output has some data")

            # Check all elements in the list of output
            for element in self._send_command_error_in_returned_output:

                # Display info message
                log.info("check_error_output: element: " + str(element))

                # Display info message
                log.info("check_error_output: output[0]: " + output[0])


                # Check if the output starts with a string with an error message (like "% Invalid input detected at '^' marker.")
                
                # Error message?
                if output.startswith(element):

                    # Yes

                    # Raise an exception
                    raise Exception(output)


    async def disable_paging(self):
        """
        Async method disabling paging on a device

        Use the "cmd_disable_paging" attribute
        """

        # Display info message
        log.info("disable_paging")
        
        # Send command to the device to disable paging
        await self.send_command(self.cmd_disable_paging)


    async def connect(self):
        """
        Async method used for connecting a device

        Currently supported: SSH and Telnet
        """

        # Display info message
        log.info("connect")

        try:

            # SSH?
            if self._protocol == "ssh":

                # Yes

                # Then Connect using SSH
                await self.connectSSH()

            # Telnet?
            elif self._protocol == "telnet":

                # Yes

                # Then Connect using Telnet
                await self.connectTelnet()
            
            else:

                # Unsupported protocol

                # Raise an exception
                raise Exception("connect: unsupported protocol: " + str(self._protocol))
        
        except Exception:

            # There was a problem with a connection method

            # Display info message
            log.info("connect: connection error")
            
            raise


    async def connectSSH(self):
        """
        Async method used for connecting a device using SSH protocol
        """

        # Display info message
        log.info("connectSSH")

        # Parameters of the connection       
        generator = asyncssh.connect(self.ip,
                                    username = self.username,
                                    password = self.password,
                                    known_hosts=None)


        # Trying to connect to the device
        try:

            self.conn = await asyncio.wait_for(generator, timeout=self.timeout)

        except asyncio.exceptions.TimeoutError as error:
             
            # Timeout

            # Display error message
            log.error("connectSSH: connection failed: timeout: '" + str(error) + "'")

            # Exception propagation
            raise asyncio.exceptions.TimeoutError("Connection failed: connection timed out.")
        
        except Exception as error:

            # Connection failed

            # Display error message
            log.error("connectSSH: connection failed: '" + str(error) + "'")

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

                # Read the prompt
                data += await asyncio.wait_for(self.stdoutx.read(MAX_BUFFER_DATA), timeout=self.timeout)

                # Display info message
                log.info("connectSSH: data: '" + str(data) + "'")

                # Check if an initial prompt is found
                for prompt in self._connect_first_ending_prompt:
                    
                    # Ending prompt found?
                    if data.endswith(prompt):

                        # Yes

                        # Display info message
                        log.info("connectSSH: first ending prompt found: '" + str(prompt) + "'")

                        # A ending prompt has been found
                        prompt_not_found = False

                        # Leave the loop
                        break


        except Exception as error:
            
            # Fail while reading the prompt

            # Display error message
            log.error("connectSSH: timeout while reading the prompt: '" + str(error) + "'")

            # Exception propagation
            raise


        # Find prompt
        self.prompt = self.find_prompt(str(data))

        # Display info message
        log.info("connectSSH: prompt found: '" + str(self.prompt) + "'")

        # Disable paging command available?
        if self.cmd_disable_paging:
            # Yes

            # Disable paging
            await self.disable_paging()



    async def connectTelnet(self):
        """
        Async method used for connecting a device using Telnet protocol
        """

        # Display info message
        log.info("connectTelnet")


        try:

            # Prepare connection with Telnet
            conn = asyncio.open_connection(self.ip, self.port)

        except Exception as error:

            # Preparation to the connection failed

            # Display error message
            log.error("connectTelnet: preparation to the connection failed: '" + str(error) + "'")

            # Exception propagation
            raise

        # Display info message
        log.info("connectTelnet: preparation to the connection success")

        try:

            # Connection with Telnet
            self._reader, self._writer = await asyncio.wait_for(conn, timeout = self.timeout)
        
        except asyncio.TimeoutError:

            # Time out during connection

            # Display error message
            log.error("connectTelnet: connection: timeout")

            # Exception propagation
            raise

        # Display info message
        log.info("connectTelnet: connnection success")

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

            # Read returned prompt
            byte_data += await asyncio.wait_for(self._reader.read(MAX_BUFFER_DATA), timeout=self.timeout)

            # Display info message
            log.info("connectTelnet: byte_data: " + str(byte_data))

            # Temporary convertion in string. This string has the following form: "b'....'"
            output = str(byte_data)
            
            # Display info message
            log.info("connectTelnet: output: " + str(output))

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
                


        # Display info message
        log.info("connectTelnet: login prompt: '" + str(output) + "'")


        # Login to use?
        if use_login:

            # Yes

            # Display info message
            log.info("connectTelnet: sending login")

            try:

                # Send login
                await self.send_command(self.username, prompt_password)

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
            output = await self.telnet_send_command_with_unexpected_pattern(self.password,
                                                                            self._connect_first_ending_prompt,
                                                                            self._telnet_connect_authentication_fail_prompt)

        except Exception:

            # Problem with the password

            # Propagate the exception
            raise

        # Display info message
        log.info("connectTelnet: password sent")

        # Find prompt
        self.prompt = self.find_prompt(str(output))

        # Display info message
        log.info("connectTelnet: prompt found: '" + str(self.prompt) + "'")


        # Password enable?
        if self.enable_mode:
            
            # Yes

            # Display info message
            log.info("connectTelnet: enable mode to be activated")

            try:

                # Send enable command
                await self.send_command(self.cmd_enable, prompt_password)

                # Display info message
                log.info("connectTelnet: enable command sent")

                # Display info message
                log.info("connectTelnet: sending enable password")

                # Send enable password
                await self.telnet_send_command_with_unexpected_pattern(self.enable_password,
                                                                        self._connect_first_ending_prompt,
                                                                        self._telnet_connect_authentication_fail_prompt)

                # Display info message
                log.info("connectTelnet: enable password sent")
            
            except Exception:

                # Problem with the enable password

                # Display info message
                log.info("connectTelnet: enable password failure")

                # Propagate the exception
                raise
        

        # Disable paging command available?
        if self.cmd_disable_paging:
            
            # Yes

            # Disable paging
            await self.disable_paging()


    async def disconnect(self):
        """
        Async method used to disconnect a device

        If this method is not used then exceptions will happen
        when the program will end
        """

        # Debug info message
        log.info("disconnect")


        # SSH?
        if self._protocol == "ssh":

            # Yes

            # Then disconnect using SSH
            await self.disconnectSSH()

        # Telnet?
        elif self._protocol == "telnet":

            # Yes

            # Then disconnect using Telnet
            await self.disconnectTelnet()
        
        else:

            # Unsupported protocol

            # Raise an exception
            raise Exception("Unsupported protocol: " + str(self._protocol))


    async def disconnectSSH(self):
        """
        Async method used to disconnect a device in SSH

        If this method is not used then exceptions will happen
        when the program will end
        """

        # Debug info message
        log.info("disconnectSSH")

        # Connection previously open in SSH?
        if self.conn:

            # Yes

            # Then close the SSH connection
            self.conn.close()

            # No more connection to disconnect
            self.conn = None


    async def disconnectTelnet(self):
        """
        Async method used to disconnect a device in Telnet

        If this method is not used then exceptions will happen
        when the program will end
        """

        # Debug info message
        log.info("disconnectTelnet")

        # Connection previously open in Telnet?
        if self._writer:

            # Yes

            # Then close the SSH connection
            self._writer.close()

            # No more connection to disconnect
            self._writer = None


    async def send_command(self, cmd, pattern = None):
        """
        Async method used to send data to a device

        :param cmd: command to send
        :type cmd: str

        :param pattern: optional, a pattern replacing the prompt when the prompt is not expected
        :type cmd: str

        :return: the output of command
        :rtype: str
        """

        # Debug info message
        log.info("send_command")

        # SSH?
        if self._protocol == "ssh":

            # Yes

            # Then disconnect using SSH
            output = await self.send_commandSSH(cmd, pattern)

        # Telnet?
        elif self._protocol == "telnet":

            # Yes

            # Then disconnect using Telnet
            output = await self.send_commandTelnet(cmd, pattern)
        
        else:

            # Unsupported protocol

            # Raise an exception
            raise Exception("send_command: unsupported protocol: " + str(self._protocol))

        # Return the result of the command
        return output


    async def send_commandSSH(self, cmd, pattern = None):
        """
        Async method used to send data to a device

        :param cmd: command to send
        :type cmd: str

        :param pattern: optional, a pattern replacing the prompt when the prompt is not expected
        :type pattern: str

        :return: the output of command
        :rtype: str
        """

        # Debug info message
        log.info("send_commandSSH")

        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        # Debug info message
        log.info("send_commandSSH: cmd = '" + str(cmd) + "'")

        # Sending command
        self.stdinx.write(cmd)

        # Display message
        log.info("send_commandSSH: command sent")
        
        # Variable used to gather data
        output = ""
        
        # Reading data
        while True:

            # Read the data received
            output += await asyncio.wait_for(self.stdoutx.read(MAX_BUFFER_DATA), timeout=self.timeout)
            
            # Debug info message
            log.info("send_commandSSH: output: '" + str(output) + "'")

            # Is a patten used?
            if pattern:

                # Use pattern instead of prompt
                if pattern in output:

                    # Yes

                    # Leave the loop
                    break                

            else:
                # Check if prompt is found
                if self.check_if_prompt_is_found(output):

                    # Yes

                    # Leave the loop
                    break

            
        # Debug info message
        log.info("send_commandSSH: raw output: '" + str(output) + "'\nsend_commandSSH: raw output (hex): '" + output.encode().hex() + "'")

        # Remove the command sent from the result of the command
        output = self.remove_command_in_output(output, str(cmd))
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        output = self.remove_ending_prompt_in_output(output)

        # Debug info message
        log.info("send_commandSSH: cleaned output: '" + str(output) + "'\nsend_commandSSH: cleaned output (hex): '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)

        # Return the result of the command
        return output


    async def send_commandTelnet(self, cmd, pattern = None):
        """
        Async method used to send data to a device

        :param cmd: command to send
        :type cmd: str

        :param pattern: optional, a pattern replacing the prompt when the prompt is not expected
        :type pattern: str

        :return: the output of command
        :rtype: str
        """

        # Debug info message
        log.info("send_commandTelnet")

        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        # Sending command
        self._writer.write(cmd.encode())



        # Temporary string variable
        output = ""

        # Temporary bytes variable
        byte_data = b""

        try:

            # Read data
            while True:

                # Read returned prompt
                byte_data += await asyncio.wait_for(self._reader.read(MAX_BUFFER_DATA), timeout=self.timeout)

                # Display info message
                log.info("send_commandTelnet: byte_data: '" + str(byte_data) + "'")

                # Temporary convertion in string. This string has the following form: "b'....'"
                output = str(byte_data)
                
                # Display info message
                log.info("send_commandTelnet: output: '" + str(output) + "'")

                
                # Is a patten used?
                if pattern:

                    # Use pattern instead of prompt
                    if pattern in output:

                        # Yes

                        # Leave the loop
                        break                

                else:

                    # Check if prompt is found
                    if self.check_if_prompt_is_found(output):

                        # Yes

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
            log.error("send_commandTelnet: error: " + str(error))

            # Exception propagation
            raise


        # Convert data (bytes) into string
        output = byte_data.decode("utf-8", "ignore")

        # Debug info message
        log.info("send_commandTelnet: raw output: '" + str(output) + "'\nsend_commandTelnet: raw output (hex): '" + output.encode().hex() + "'")

        # Remove the command sent from the result of the command
        output = self.remove_command_in_output(output, str(cmd))
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        output = self.remove_ending_prompt_in_output(output)

        # Debug info message
        log.info("send_commandTelnet: cleaned output: '" + str(output) + "'\nsend_commandTelnet: cleaned output (hex): '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)

        # Return the result of the command
        return output



    async def telnet_send_command_with_unexpected_pattern(self, cmd, pattern, error_pattern = None):
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

        :param error_pattern: optional, a list of failed prompts found when the login and password are not correct
        :type error_pattern: str

        :return: the output of command
        :rtype: str
        """

        # Debug info message
        log.info("telnet_send_command_with_unexpected_pattern")

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
                byte_data += await asyncio.wait_for(self._reader.read(MAX_BUFFER_DATA), timeout=self.timeout)

                # Display info message
                log.info("telnet_send_command_with_unexpected_pattern: byte_data: '" + str(byte_data) + "'")

                # Temporary convertion in string. This string has the following form: "b'....'"
                output = str(byte_data)
                
                # Display info message
                log.info("telnet_send_command_with_unexpected_pattern: output: '" + str(output) + "'")

                
                # Is a pattern used?
                if pattern:

                    # Check all pattern of prompt in the output
                    for prompt in pattern:

                        # Display info message
                        log.info("telnet_send_command_with_unexpected_pattern: checking prompt: '" + str(prompt) + "'")

                        # A pattern found?
                        if prompt in output:

                            # Yes

                            # A pattern is found. The main loop can be stopped
                            pattern_not_found =  False

                            # Display info message
                            log.info("telnet_send_command_with_unexpected_pattern: prompt found: '" + str(prompt) + "'")

                            # Leave the loop
                            break

                # Is an unexpected pattern used?
                if error_pattern and pattern_not_found:

                    # Check all unexpected pattern of prompt in the output
                    for bad_prompt in error_pattern:

                        # Display info message
                        log.info("telnet_send_command_with_unexpected_pattern: checking unexpected prompt: '" + str(bad_prompt) + "'")

                        # An error_pattern pattern found?
                        if bad_prompt in output:

                            # Yes

                            # Display error message
                            log.error("telnet_send_command_with_unexpected_pattern: authentication failed")

                            # Raise exception
                            raise Exception("telnet_send_command_with_unexpected_pattern: authentication failed")

                            # Leave the loop
                            #break


        except asyncio.TimeoutError:

            # Time out during when reading prompt

            # Close the connection in order to not display RuntimeError
            await self.disconnect()

            # Display error message
            log.error("telnet_send_command_with_unexpected_pattern: reading prompt: timeout")

            # Exception propagation
            raise


        except Exception as error:

            # Error during when reading prompt

            # Close the connection in order to not display RuntimeError
            await self.disconnect()

            # Display error message
            log.error("telnet_send_command_with_unexpected_pattern: reading prompt: error: " + str(error))

            # Exception propagation
            raise


        # Convert data (bytes) into string
        output = byte_data.decode("utf-8", "ignore")

        # Debug info message
        log.info("telnet_send_command_with_unexpected_pattern: raw output: '" + str(output) + "'\ntelnet_send_command_with_unexpected_pattern: raw output (hex): '" + output.encode().hex() + "'")

        # Remove the command sent from the result of the command
        output = self.remove_command_in_output(output, str(cmd))
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        output = self.remove_ending_prompt_in_output(output)

        # Debug info message
        log.info("telnet_send_command_with_unexpected_pattern: cleaned output: '" + str(output) + "'\ntelnet_send_command_with_unexpected_pattern: cleaned output (hex): '" + output.encode().hex() + "'")

        # Return the result of the command
        return output




    async def send_config_set(self, cmds=None):
        """
        Async method used to send command in config mode

        The commands send can be either a string a a list of strings. There are
        3 steps:
        - Entering configuration mode
        - Sending the commands
        - Leaving configuration mode

        :param cmds: The commands to the device
        :type cmds: str or list

        :return: the results of the commands sent
        """

        # Display info message
        log.info("send_config_set")


        # Debug info message
        log.info("send_command")

        # SSH?
        if self._protocol == "ssh":

            # Yes

            # Then disconnect using SSH
            output = await self.send_config_setSSH(cmds)

        # Telnet?
        elif self._protocol == "telnet":

            # Yes

            # Then disconnect using Telnet
            output = await self.send_config_setTelnet(cmds)
        
        else:

            # Unsupported protocol

            # Raise an exception
            raise Exception("send_config_set: unsupported protocol: " + str(self._protocol))

        # Return the result of the commands
        return output




    async def send_config_setSSH(self, cmds=None):
        """
        Async method used to send command in config mode

        The commands send can be either a string a a list of strings. There are
        3 steps:
        - Entering configuration mode
        - Sending the commands
        - Leaving configuration mode

        :param cmds: The commands to the device
        :type cmds: str or list

        :return: the results of the commands sent
        """

        # Display info message
        log.info("send_config_setSSH")

        # Clear returned output
        returned_output  = ""

        # Check if cmds is a string
        if isinstance(cmds, str):

            # A string

            # Convert the string into a list
            cmds = [cmds]

            # A list?
        elif not isinstance(cmds, list):

            # Not a list (and not a string)

            # Display error message
            log.error("send_config_setSSH: parameter cmds used in send_config_set is neither a string or a list")            

            # Leave the method
            return returned_output


        ##############################
        # Entering configuration mode
        ##############################

        # Display info message
        log.info("send_config_set: entering configuration mode")

        # Clear output
        output  = ""

        # Get command for entering in config made
        cmd = self.cmd_enter_config_mode
        
        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        # Display info message
        log.info("send_config_setSSH: cmd = '" + str(cmd) + "'")

        # Sending command
        self.stdinx.write(cmd)

        # Display message
        log.info("send_config_setSSH: configuration mode entered")

        while True:
            
            # Read the data received
            output += await asyncio.wait_for(self.stdoutx.read(MAX_BUFFER_DATA), timeout=self.timeout)
            
            # Display info message
            log.info("send_config_setSSH: output: '" + str(output) + "'")

            # Check if prompt is found
            if self.check_if_prompt_is_found(output):

                # Yes

                # Leave the loop
                break

        # Debug info message
        log.info("send_config_setSSH: raw output: '" + str(output) + "'\nsend_config_setSSH: raw output (hex): '" + output.encode().hex() + "'")

        # Add the output to the returned output
        returned_output += output

        # Remove the command sent from the result of the command
        output = self.remove_command_in_output(output, str(cmd))
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        output = self.remove_ending_prompt_in_output(output)

        # Display info message
        log.info("send_config_setSSH: cleaned output: '" + str(output) + "'\nsend_config_setSSH: cleaned output (hex): '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)




        ##############################
        # Sending commands
        ##############################

        # Display info message
        log.info("send_config_setSSH: sending commands")

        # Clear output
        output  = ""

        # Each command
        for cmd in cmds:

            # Add carriage return at the end of the command (mandatory to send the command)
            cmd = cmd + "\n"

            # Display info message
            log.info("send_config_setSSH: cmd = '" + str(cmd) + "'")

            # Sending command
            self.stdinx.write(cmd)

            # Display info message
            log.info("send_config_setSSH: command sent")

            while True:
                
                # Read the data received
                output += await asyncio.wait_for(self.stdoutx.read(MAX_BUFFER_DATA), timeout=self.timeout)
                
                # Display info message
                log.info("send_config_setSSH: output: '" + str(output) + "'")

                # Check if prompt is found
                if self.check_if_prompt_is_found(output):

                    # Yes

                    # Leave the loop
                    break

            # Debug info message
            log.info("send_config_setSSH: raw output: '" + str(output) + "'\nsend_config_setSSH: raw output (hex): '" + output.encode().hex() + "'")

            # Add the output to the returned output
            returned_output += output

            # Remove the command sent from the result of the command
            output = self.remove_command_in_output(output, str(cmd))
            # Remove the carriage return of the output
            output = self.remove_starting_carriage_return_in_output(output)
            # Remove the ending prompt of the output
            output = self.remove_ending_prompt_in_output(output)

            # Display info message
            log.info("send_config_setSSH: cleaned output: '" + str(output) + "'\nsend_config_setSSH: cleaned output (hex): '" + output.encode().hex() + "'")

            # Check if there is an error in the output string (like "% Unrecognized command")
            # and generate an exception if needed
            self.check_error_output(output)




        ##############################
        # Leaving configuration mode
        ##############################

        # Display info message
        log.info("send_config_setSSH: leaving configuration mode")

        # Clear output
        output  = ""

        # Get command to leave config made
        cmd = self.cmd_exit_config_mode

        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        # Display info message
        log.info("send_config_setSSH: cmd = '" + str(cmd) + "'")

        # Sending command
        self.stdinx.write(cmd)

        # Display info message
        log.info("send_config_setSSH: command to leave configuration mode sent")


        while True:
            
            # Read the data received
            output += await asyncio.wait_for(self.stdoutx.read(MAX_BUFFER_DATA), timeout=self.timeout)
            
            # Display info message
            log.info("send_config_setSSH: output: '" + str(output) + "'")

            # Check if prompt is found
            if self.check_if_prompt_is_found(output):

                # Yes

                # Leave the loop
                break

        # Debug info message
        log.info("send_config_setSSH: raw output: '" + str(output) + "'\nsend_config_setSSH: raw output (hex): '" + output.encode().hex() + "'")

        # Add the output to the returned output
        returned_output += output

        # Remove the command sent from the result of the command
        output = self.remove_command_in_output(output, str(cmd))
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        output = self.remove_ending_prompt_in_output(output)

        # Display info message
        log.info("send_config_setSSH: cleaned output: '" + str(output) + "'\nsend_config_setSSH: cleaned output (hex): '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)


        # Return the result of the commands
        return returned_output





    async def send_config_setTelnet(self, cmds=None):
        """
        Async method used to send command in config mode

        The commands send can be either a string a a list of strings. There are
        3 steps:
        - Entering configuration mode
        - Sending the commands
        - Leaving configuration mode

        :param cmds: The commands to the device
        :type cmds: str or list

        :return: the results of the commands sent
        """

        # Display info message
        log.info("send_config_setTelnet")

        # Clear returned output
        returned_output  = ""

        # Check if cmds is a string
        if isinstance(cmds, str):

            # A string

            # Convert the string into a list
            cmds = [cmds]

            # A list?
        elif not isinstance(cmds, list):

            # Not a list (and not a string)

            # Display error message
            log.error("send_config_setTelnet: parameter cmds used in send_config_set is neither a string or a list")            

            # Leave the method
            return returned_output


        ##############################
        # Entering configuration mode
        ##############################

        # Display info message
        log.info("send_config_setTelnet: entering configuration mode")

        # Clear output
        output  = ""

        # Get command for entering in config made
        cmd = self.cmd_enter_config_mode
        
        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        # Display info message
        log.info("send_config_setTelnet: cmd = '" + str(cmd) + "'")

        # Sending command
        self._writer.write(cmd.encode())

        # Display message
        log.info("send_config_setTelnet: configuration mode entered")

        # Temporary string variable
        output = ""

        # Temporary bytes variable
        byte_data = b""

        try:

            # Read data
            while True:
                
                # Read the data received
                byte_data += await asyncio.wait_for(self._reader.read(MAX_BUFFER_DATA), timeout=self.timeout)
                
                # Temporary convertion in string. This string has the following form: "b'....'"
                output = str(byte_data)
                
                # Display info message
                log.info("send_config_setTelnet: output: '" + str(output) + "'")

                # Check if prompt is found
                if self.check_if_prompt_is_found(output):

                    # Yes

                    # Leave the loop
                    break


        except asyncio.TimeoutError:

            # Time out during when reading prompt

            # Display error message
            log.error("send_config_setTelnet: connection: timeout")

            # Exception propagation
            raise


        except Exception as error:

            # Error during when reading prompt
            
            # Display error message
            log.error("send_config_setTelnet: error: " + str(error))

            # Exception propagation
            raise


        # Convert data (bytes) into string
        output = byte_data.decode("utf-8", "ignore")

        # Debug info message
        log.info("send_config_setTelnet: raw output: '" + str(output) + "'\nsend_config_setTelnet: raw output (hex): '" + output.encode().hex() + "'")

        # Add the output to the returned output
        returned_output += output

        # Remove the command sent from the result of the command
        output = self.remove_command_in_output(output, str(cmd))
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        output = self.remove_ending_prompt_in_output(output)

        # Display info message
        log.info("send_config_setTelnet: cleaned output: '" + str(output) + "'\nsend_config_setTelnet: cleaned output (hex): '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)




        ##############################
        # Sending commands
        ##############################

        # Display info message
        log.info("send_config_setTelnet: sending commands")

        # Clear output
        output  = ""

        # Each command
        for cmd in cmds:

            # Add carriage return at the end of the command (mandatory to send the command)
            cmd = cmd + "\n"

            # Display info message
            log.info("send_config_setTelnet: cmd = '" + str(cmd) + "'")

            # Sending command
            self._writer.write(cmd.encode())

            # Display info message
            log.info("send_config_setTelnet: command sent")

            # Temporary string variable
            output = ""

            # Temporary bytes variable
            byte_data = b""

            try:

                # Read data
                while True:
                    
                    # Read the data received
                    byte_data += await asyncio.wait_for(self._reader.read(MAX_BUFFER_DATA), timeout=self.timeout)
                    
                    # Temporary convertion in string. This string has the following form: "b'....'"
                    output = str(byte_data)
                    
                    # Display info message
                    log.info("send_config_setTelnet: output: '" + str(output) + "'")

                    # Check if prompt is found
                    if self.check_if_prompt_is_found(output):

                        # Yes

                        # Leave the loop
                        break

            except asyncio.TimeoutError:

                # Time out during when reading prompt

                # Display error message
                log.error("send_config_setTelnet: connection: timeout")

                # Exception propagation
                raise


            except Exception as error:

                # Error during when reading prompt
                
                # Display error message
                log.error("send_config_setTelnet: error: " + str(error))

                # Exception propagation
                raise


            # Convert data (bytes) into string
            output = byte_data.decode("utf-8", "ignore")

            # Debug info message
            log.info("send_config_setTelnet: raw output: '" + str(output) + "'\nsend_config_setTelnet: raw output (hex): '" + output.encode().hex() + "'")

            # Add the output to the returned output
            returned_output += output

            # Remove the command sent from the result of the command
            output = self.remove_command_in_output(output, str(cmd))
            # Remove the carriage return of the output
            output = self.remove_starting_carriage_return_in_output(output)
            # Remove the ending prompt of the output
            output = self.remove_ending_prompt_in_output(output)

            # Display info message
            log.info("send_config_setTelnet: cleaned output: '" + str(output) + "'\nsend_config_setTelnet: cleaned output (hex): '" + output.encode().hex() + "'")

            # Check if there is an error in the output string (like "% Unrecognized command")
            # and generate an exception if needed
            self.check_error_output(output)




        ##############################
        # Leaving configuration mode
        ##############################

        # Display info message
        log.info("send_config_setTelnet: leaving configuration mode")

        # Clear output
        output  = ""

        # Get command to leave config made
        cmd = self.cmd_exit_config_mode

        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        # Display info message
        log.info("send_config_setTelnet: cmd = '" + str(cmd) + "'")

        # Sending command
        self._writer.write(cmd.encode())

        # Display info message
        log.info("send_config_setTelnet: command to leave configuration mode sent")


        # Temporary string variable
        output = ""

        # Temporary bytes variable
        byte_data = b""

        # Protection against infinite loop
        loop = 3

        try:

            # Read data
            while loop:
                
                # Read the data received
                byte_data += await asyncio.wait_for(self._reader.read(MAX_BUFFER_DATA), timeout=self.timeout)
                
                # Temporary convertion in string. This string has the following form: "b'....'"
                output = str(byte_data)
                
                # Display info message
                log.info("send_config_setTelnet: output: '" + str(output) + "'")

                await asyncio.sleep(0.5)

                # Check if prompt is found
                if self.check_if_prompt_is_found(output):

                    # Yes

                    # Leave the loop
                    break

                # Protection for "exit" command infinite loop in Cisco when enable is not activated
                loop -= 1

        except asyncio.TimeoutError:

            # Time out during when reading prompt

            # Display error message
            log.error("send_config_setTelnet: connection: timeout")

            # Exception propagation
            raise


        except Exception as error:

            # Error during when reading prompt
            
            # Display error message
            log.error("send_config_setTelnet: error: " + str(error))

            # Exception propagation
            raise


        # Convert data (bytes) into string
        output = byte_data.decode("utf-8", "ignore")

        # Debug info message
        log.info("send_config_setTelnet: raw output: '" + str(output) + "'\nsend_config_setTelnet: raw output (hex): '" + output.encode().hex() + "'")

        # Add the output to the returned output
        returned_output += output

        # Remove the command sent from the result of the command
        output = self.remove_command_in_output(output, str(cmd))
        # Remove the carriage return of the output
        output = self.remove_starting_carriage_return_in_output(output)
        # Remove the ending prompt of the output
        output = self.remove_ending_prompt_in_output(output)

        # Display info message
        log.info("send_config_setTelnet: cleaned output: '" + str(output) + "'\nsend_config_setTelnet: cleaned output (hex): '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)


        # Return the result of the commands
        return returned_output






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

        # Seek "Version " and "," to get the version in the returned output
        version = output.split("Version ")[1].split(",")[0]

        # Display info message
        log.info("get_version: version: " + version)

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
        log.info("get_hostname: output: '" + str(output) + "'")

        # Remove the useless information in the returned string
        output = output.split()[0]

        # Display info message
        log.info("get_hostname: hostname found: '" + str(output) + "'")

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
        log.info("get_model: output: '" + str(output) + "'")

        # Remove the useless information in the returned string
        output = output.split('"')[3]

        # Display info message
        log.info("get_model: model found: '" + str(output) + "'")

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
        log.info("get_serial_number: output: '" + str(output) + "'")

        # Remove the useless information in the returned string
        output = output.splitlines()[0].split()[-1]

        # Display info message
        log.info("get_hostname: hostname found: '" + str(output) + "'")

        # Return the serial number of the device
        return output

    async def get_config(self):
        """
        Asyn method used to get the configuration of the device

        :return: Configuration of the device
        :rtype: str
        """

        # Display info message
        log.info("get_config")

        # Get config
        output = await self.send_command(self.cmd_get_config)

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

        # Send command
        output = await self.send_command(self.cmd_save_config)

        # Return the commands of the configuration saving process
        return output

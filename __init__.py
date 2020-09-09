# Python library import
import asyncio, asyncssh, sys
import logging

# Debug level
#logging.basicConfig(level=logging.WARNING)
logging.basicConfig(level=logging.INFO)
asyncssh.set_debug_level(1)

# Declaration of constant values

# Version
__version__ = "0.0.1"


#cisco_s300


async def ConnectDevice(**kwargs):

    my_class = NetworkDevice(**kwargs)

    await my_class.connect()

    return my_class




class Exception_Error_in_output(Exception):
    """
    Class used for exceptions when the content of the output returned is having
    an error
    """
    #print("...Unrecognized command...")
    pass

class NetworkDevice:

    def __init__(self, **kwargs):

        print("__init__")

        self.ip = ""
        self.username = ""
        self.password = ""
        self.device_type = ""
        self.port = 22
        self.timeout = 5
        self.cmd_disable_pagging = "terminal datadump"
        self.cmd_enter_config_mode = "configure terminal"
        self.cmd_exit_config_mode = "exit"
        self.cmd_get_version = "show version"
        self.cmd_get_hostname = "show system | include System Name:"
        self.cmd_get_model = "show system | b Type"
        self.cmd_get_serial_number = "show system id unit 1"
        self.cmd_get_config = "show running-config"
        

        self.possible_prompts = []


        print(kwargs)

        if 'ip' in kwargs:
            self.ip = kwargs['ip']
            logging.info("ip found" + str(self.ip))

        if 'username' in kwargs:
            self.username = kwargs['username']
            logging.info("username found: " + str(self.username))
        
        if 'password' in kwargs:
            self.password = kwargs['password']
            logging.info("password found: " + str(self.password))

        if 'device_type' in kwargs:
            self.device_type = kwargs['device_type']
            logging.info("device_type found: " + str(self.device_type))

        if 'port' in kwargs:
            self.port = kwargs['port']
            logging.info("port found: " + str(self.port))



    def find_prompt(self, text):

        #print(type(text))

        # Get last line of the data
        prompt = text.split()[-1]

        print(prompt)

        # Get the possible prompts for future recognition
        self.possible_prompts = self.get_possible_prompts(prompt)

        return prompt

    def get_possible_prompts(self, prompt):

        list_of_prompts = []

        list_of_possible_ending_prompts = [
            "(config-if)#",
            "(config)#",
            ">",
            "#",
        ]

        my_prompt = prompt

        # First, remove ending of the prompt (i.e '#', '>', "(config-if)#", "(config)#")
        for ending in list_of_possible_ending_prompts:

            # Is a prompt ending found?
            if my_prompt.endswith(ending):

                # Yes

                # Then remove the ending
                my_prompt = my_prompt[:-len(ending)]

                # Break the loop
                break


        # Prompt should be from "switch#" to "switch"

        print("My prompt: " + my_prompt)

        # Now create all the possible prompts for that device
        for ending in list_of_possible_ending_prompts:

            # Save the prompt name with a possible ending in the list
            list_of_prompts.append(my_prompt + ending)


        print("list of prompts: " + str(list_of_prompts))



        return list_of_prompts


    def check_if_prompt_is_found(self, text):

        # By default the prompt is not found
        prompt_found = False

        # Check all possible prompts
        for prompt in self.possible_prompts:

            print("...prompt: '" + str(prompt) + "'")

            # Is this prompt present in the text?
            if prompt in text:

                # Yes
                prompt_found = True

                # Leave the for loop
                break
        
        return prompt_found




    def remove_command_in_output(self, text, cmd):


        print("cmd = '" + str(cmd) + "'")
        print("cmd = '" + cmd.encode().hex() + "'")
        output = text.lstrip(cmd)

        return output

    def remove_starting_carriage_return_in_output(self, text):


        output = text.lstrip("\r\n\r")

        return output

    def remove_ending_prompt_in_output(self, text):

        print("..Before remove_ending_prompt_in_output:\n'" + text + "'")

        # Check all possible prompts
        for prompt in self.possible_prompts:

            print("...prompt: '" + str(prompt) + "'")

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

        print("..After remove_ending_prompt_in_output:\n'" + text + "'")

        return text

    def check_error_output(self, output):
        """
        Check if an error is returned by the device ("% Unrecognized command", "% Ambiguous command", etc.)
        """

        # Check if output has some data
        if output:

            # Yes

            print("...output[0]: " + output[0])

            # Error message?
            if output[0] == "%":

                # Yes

                # Raise an exception
                raise Exception_Error_in_output(output)


    async def disable_paging(self):

        

        print("disable_paging")
        
        # Send command to the device to disable pagging
        await self.send_command(self.cmd_disable_pagging)



    async def connect(self):

        print("123")

        #generator = asyncssh.connect('192.168.0.254', username='cisco', password="Cisco1234")        
        generator = asyncssh.connect(self.ip, username = self.username, password = self.password)


        # Read the prompt
        try:
            self.conn = await asyncio.wait_for(generator, timeout=5)
        except Exception:
            print("....Timeout during connect....")

        # Display message
        print("...Connection...")

        # Create a session
        self.stdinx, self.stdoutx, _ = await self.conn.open_session(term_type="spooky")

        # Display message
        print("...after open_session()...")


        # Read the prompt
        try:
            #data = await asyncio.wait_for(stdoutx.readuntil(PROMPT), timeout=1)
            data = await asyncio.wait_for(self.stdoutx.read(4096), timeout=1)

        except Exception:
            print("....Timeout while reading the prompt....")


        # Find prompt
        self.prompt = self.find_prompt(str(data))

        # Display message
        print("...Find prompt...'" + str(self.prompt) + "'")

        # Disable paging
        await self.disable_paging()


    async def disconnect(self):

        print("456")

        if self.conn:

            self.conn.close()


    async def send_command(self, cmd):

        
        print("789")

        # Add carriage return at the end of the command (mandatory to send the command)
        cmd = cmd + "\n"

        print("cmd = '" + str(cmd) + "'")

        
        # Sending command
        self.stdinx.write(cmd)

        # Display message
        print("...after stdout.write...")
        
        # Wait before reading so that full data can be read
        #await asyncio.sleep(1)
        
        # Reading data
        #data = await stdoutx.read(4096)
        """
        try:
            output = await asyncio.wait_for(self.stdoutx.readuntil(self.prompt), timeout=2)
        except Exception:
            print("....Timeout while reading the prompt....")
        """

        output = ""

        #output = await asyncio.wait_for(self.stdoutx.readuntil(self.prompt), timeout=2)
        

        
        while True:
            print("while 1")
            
            # Read the data received
            output += await asyncio.wait_for(self.stdoutx.read(65535), timeout=self.timeout)
            
            print("output: '" + str(output) + "'")

            # Check if prompt is found
            if self.check_if_prompt_is_found(output):

                # Yes

                # Leave the loop
                break


            

        print("output 1: '" + str(output) + "'")


        print("output 1: '" + output.encode().hex() + "'")

        output = self.remove_command_in_output(output, str(cmd))
        output = self.remove_starting_carriage_return_in_output(output)
        output = self.remove_ending_prompt_in_output(output)

        print("output 2: '" + str(output) + "'")

        print("output 2: '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)


        return output

    async def send_config_set(self, cmds=None):

        print("...send_config_set...")

        # Check if cmds is a string
        if isinstance(cmds, str):

            # A string

            # Convert the string into a list
            cmds = [cmds]

            # A list?
        elif not isinstance(cmds, list):

            # Not a list

            # Leave the method
            return ""


        ##############################
        # Entering configuration mode
        ##############################

        # Clear output
        output  = ""

        # Get command for entering in config made
        cmd = self.cmd_enter_config_mode

        cmd = cmd + "\n"

        print("cmd = '" + str(cmd) + "'")

        
        # Sending command
        self.stdinx.write(cmd)

        # Display message
        print("...after stdout.write...")


        while True:
            print("while 1")
            
            # Read the data received
            output += await asyncio.wait_for(self.stdoutx.read(65535), timeout=self.timeout)
            
            print("output: '" + str(output) + "'")

            # Check if prompt is found
            if self.check_if_prompt_is_found(output):

                # Yes

                # Leave the loop
                break


            

        print("output 1: '" + str(output) + "'")


        print("output 1: '" + output.encode().hex() + "'")


        output = self.remove_command_in_output(output, str(cmd))
        output = self.remove_starting_carriage_return_in_output(output)
        output = self.remove_ending_prompt_in_output(output)

        print("output 2: '" + str(output) + "'")

        print("output 2: '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)


        ##############################
        # Sending commands
        ##############################

        # Clear output
        output  = ""

        # Each command
        for cmd in cmds:

            cmd = cmd + "\n"

            print("cmd = '" + str(cmd) + "'")

            
            # Sending command
            self.stdinx.write(cmd)

            # Display message
            print("...after stdout.write...")


            while True:
                print("while 1")
                
                # Read the data received
                output += await asyncio.wait_for(self.stdoutx.read(65535), timeout=self.timeout)
                
                print("output: '" + str(output) + "'")

                # Check if prompt is found
                if self.check_if_prompt_is_found(output):

                    # Yes

                    # Leave the loop
                    break


                

            print("output 1: '" + str(output) + "'")


            print("output 1: '" + output.encode().hex() + "'")


            output = self.remove_command_in_output(output, str(cmd))
            output = self.remove_starting_carriage_return_in_output(output)
            output = self.remove_ending_prompt_in_output(output)

            print("output 2: '" + str(output) + "'")

            print("output 2: '" + output.encode().hex() + "'")

            # Check if there is an error in the output string (like "% Unrecognized command")
            # and generate an exception if needed
            self.check_error_output(output)








        ##############################
        # Leaving configuration mode
        ##############################

        # Clear output
        output  = ""

        # Get command to leave config made
        cmd = self.cmd_exit_config_mode

        cmd = cmd + "\n"

        print("cmd = '" + str(cmd) + "'")

        
        # Sending command
        self.stdinx.write(cmd)

        # Display message
        print("...after stdout.write...")


        while True:
            print("while 1")
            
            # Read the data received
            output += await asyncio.wait_for(self.stdoutx.read(65535), timeout=self.timeout)
            
            print("output: '" + str(output) + "'")

            # Check if prompt is found
            if self.check_if_prompt_is_found(output):

                # Yes

                # Leave the loop
                break


            

        print("output 1: '" + str(output) + "'")


        print("output 1: '" + output.encode().hex() + "'")


        output = self.remove_command_in_output(output, str(cmd))
        output = self.remove_starting_carriage_return_in_output(output)
        output = self.remove_ending_prompt_in_output(output)

        print("output 2: '" + str(output) + "'")

        print("output 2: '" + output.encode().hex() + "'")

        # Check if there is an error in the output string (like "% Unrecognized command")
        # and generate an exception if needed
        self.check_error_output(output)








        return output

    async def get_version(self):

        version = ""

        # Get version
        output = await self.send_command(self.cmd_get_version)

        # Seek "Version: "
        for line in output.splitlines():

            print("line: " + line)
            if "Version: " in line:
                version = line.split("Version: ")[1]
                break


        print("version: " + version)
        return version
           
    async def get_config(self):

        # Get config
        output = await self.send_command(self.cmd_get_config)

        return output

    async def get_hostname(self):

        # Get hostname
        output = await self.send_command(self.cmd_get_hostname)

        print("...output: '" + str(output) + "'")

        # Remove the useless information in the returned string
        output = output.split("System Name: ")[1].strip()

        return output

    async def get_model(self):

        # Get model
        output = await self.send_command(self.cmd_get_model)

        print("...output: '" + str(output) + "'")

        # Remove the useless information in the returned string
        output = output.splitlines()[2].split()[1]

        return output


    async def get_serial_number(self):
        """
        Get serial number of the switch or the serial number of the first switch of a stack
        """

        # Get model
        output = await self.send_command(self.cmd_get_serial_number)

        print("...output: '" + str(output) + "'")

        # Remove the useless information in the returned string
        output = output.lstrip("Serial number :")

        return output

async def task():



    my_device = {
        'ip':   '',
        'username': '',
        'password': '',
        'device_type': '',        
    }

    try:

        sw1 = await ConnectDevice(**my_device)

    except Exception as error:

        print("Error : " + str(error))
        sys.exit()


    #print(sw1)
    """

    # Command to send
    #cmd = "show version\n"
    cmd = "show interfaces status"

    output = await sw1.send_command(cmd)
    print("output: '" + str(output) + "'")


    output = await sw1.get_version()
    print("output: '" + str(output) + "'")

    output = await sw1.get_config()
    print("output: '" + str(output) + "'")
    
    output = await sw1.get_hostname()
    print("output: '" + str(output) + "'")

    output = await sw1.get_model()
    print("output: '" + str(output) + "'")
    

    output = await sw1.get_serial_number()
    print("output: '" + str(output) + "'")
    
    
    
    cmd = "show interfaces you smell"

    try:
        output = await sw1.send_command(cmd)
        print("output: '" + str(output) + "'")
    except Exception as error:

        print("Exception: " + str(error))

    """

    cmd = ["no vlan 3", "do sh vlan"]

    output = await sw1.send_config_set(cmd)
    print("output: '" + str(output) + "'")


    await sw1.disconnect()


# Main function call
if __name__ == '__main__':

    # Main async loop
    asyncio.run(task())






# Python library import
from netscud.base_connection import NetworkDevice, log

class CiscoIOS(NetworkDevice):
    """
    Class for Cisco IOS devices
    """
    '''
        

    User Access Verification

    Password:
    % Password:  timeout expired!
    Password:
    SW3>en
    Password:
    Password:
    SW3#
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.cmd_get_hostname = "show version | include uptime"


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
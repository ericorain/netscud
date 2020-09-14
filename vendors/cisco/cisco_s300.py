# Python library import
from netscud.base_connection import NetworkDevice

class CiscoS300(NetworkDevice):
    """
    Class for SG3XX devices
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cmd_disable_paging = "terminal datadump"
    



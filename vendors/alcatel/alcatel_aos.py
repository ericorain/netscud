# Python library import
from netscud.base_connection import NetworkDevice

class AlcatelAOS(NetworkDevice):
    """
    Class for Alcatel AOS devices
    """



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ssh_connect_first_ending_prompt = ["> "]
        self.cmd_disable_paging = ""
        self.cmd_enter_config_mode = ""
        self.cmd_exit_config_mode = ""
        self.cmd_get_version = "show system"
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

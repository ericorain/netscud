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

        self._connect_first_ending_prompt = ["> "]
        self.list_of_possible_ending_prompts = [
            "> ",
        ]
        # No global disabling for Mikrotik RouterOS so use
        # "without-paging" at the end of your commands
        self.cmd_disable_paging = None
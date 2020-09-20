# Python library import
from netscud.base_connection import NetworkDevice, log

class CiscoIOS(NetworkDevice):
    """
    Class for Cisco IOS devices
    """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self._send_command_error_in_returned_output = ["%"]


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

            # With Cisco IOS an error message can have "%" at first or second line
            ##############################
            # R1#show vl
            # % Incomplete command.
            #
            # R1#show aze
            #          ^
            # % Invalid input detected at '^' marker.
            #
            # R1#
            ##############################

            # Convertion of a string to a list of strings
            lines = output.splitlines()

            # By default no data to ccheck
            output_lines = []

            # No more than 2 lines since error messages are in forst or second line
            max_number_of_lines = 2

            # Save 2 lines maximum into a list
            for line in lines:

                # Copy the line
                output_lines.append(line)

                # Decrease the number of maximum of line
                max_number_of_lines -= 1

                # Maximum of lines reached?
                if max_number_of_lines <= 0:

                    # Yes

                    # Then break the lopp
                    break


            # Display info message
            log.info("check_error_output: number of lines in the output: " + str(len(output_lines)))

            # Check all elements in the list of output
            for element in self._send_command_error_in_returned_output:

                # Display info message
                log.info("check_error_output: element: '" + str(element) + "'")

                # Check if the output starts with a string with an error message (like "% Invalid input detected at '^' marker.")
                for line in output_lines:

                    # Display info message
                    log.info("check_error_output: line: '" + str(line) + "'")
                    
                    # Error message?
                    if line.startswith(element):

                        # Yes

                        # Display info message
                        log.info("check_error_output: error in output found : '" + str(element) + "'")

                        # Raise an exception
                        raise Exception(output)


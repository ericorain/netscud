.. _API_REF:

API
####################

netscud uses API to simplify the tasks of network programing. Those API are common commands available on devices. send_command() and send_config_set() are 2 specific API commands which are used for the other API commands.

Here is the current list of supported API:

* get_hostname()
* get_model()
* get_serial_number()
* get_version()
* save_config()

get_hostname()
**************

Get the name of a device.

Return a string value.

get_model()
***********

Get the model type of a device.

Return a string value.

get_serial_number()
*******************

Get the serial number of a device.

Return a string value.

get_version()
*************

Get the software version of a device.

Return a string value.

save_config()
*************

Save the configuration of a device.

Return a string value.

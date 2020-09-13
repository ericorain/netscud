# Python library import
from netscud.vendors.cisco.cisco_s300 import CiscoS300
from netscud.vendors.alcatel.alcatel_aos import AlcatelAOS

#  Rhe supported device_types are the keys of this dictionary
ALL_DEVICE_TYPE_CLASS = {
    "cisco_s300": CiscoS300,
    "alcatel_aos": AlcatelAOS,
}


async def ConnectDevice(**kwargs):
    """
    Async function to be used for connnecting a device
    
    This async function allows to use a class with an async method


    :param kwargs: dictionary with the device connection parameters
    :type kwargs: dict

    :return: Return the object with the 
    :rtype: object with the device class
    """


    # Device type provided in the device dictionary?
    if 'device_type' in kwargs:
        
        # Yes

        #Get device type
        device_type = kwargs['device_type']
    else:
        
        # No

        # Display error message
        raise Exception("ConnectDevice: no device type specified")

    # Check if device type is amongst the supported ones
    if device_type not in ALL_DEVICE_TYPE_CLASS:

        # Not a supported device
        
        # Display error message
        raise Exception("ConnectDevice: device type unknown: " + str(device_type))

    # Create a class
    my_class = ALL_DEVICE_TYPE_CLASS[device_type](**kwargs)

    try:
        # Run an async method to connect a device
        await my_class.connect()
    
    except Exception:

        # propagate exception if needed
        raise


    # Return the class
    return my_class
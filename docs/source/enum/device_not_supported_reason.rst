
==================================================================================================
DeviceNotSupportedReason
==================================================================================================

.. describe:: DeviceNotSupportedReason

    Reasons why a virtual device would not be supported on a host.
    
    
    .. py:data:: DeviceNotSupportedReason.guest
    
        The device is supported by the host in general, but not for the specific guest OS the virtual machine is using.
        
    
    .. py:data:: DeviceNotSupportedReason.host
    
        The host does not support this virtual device at all.
        
    
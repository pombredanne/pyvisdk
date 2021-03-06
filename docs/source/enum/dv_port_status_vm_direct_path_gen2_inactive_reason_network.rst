
==================================================================================================
DVPortStatusVmDirectPathGen2InactiveReasonNetwork
==================================================================================================

.. describe:: DVPortStatusVmDirectPathGen2InactiveReasonNetwork

    Set of possible values for vmDirectPathGen2InactiveReasonNetwork.
    
    
    .. py:data:: DVPortStatusVmDirectPathGen2InactiveReasonNetwork.portNptDisabledForPort
    
        VMDirectPath Gen 2 has been explicitly disabled for this port.
        
    
    .. py:data:: DVPortStatusVmDirectPathGen2InactiveReasonNetwork.portNptIncompatibleDvs
    
        The port's switch does not support VMDirectPath Gen 2.See vmDirectPathGen2Supported
        
    
    .. py:data:: DVPortStatusVmDirectPathGen2InactiveReasonNetwork.portNptNoCompatibleNics
    
        None of the physical NICs used as uplinks for this port support VMDirectPath Gen 2.See vmDirectPathGen2Supported
        
    
    .. py:data:: DVPortStatusVmDirectPathGen2InactiveReasonNetwork.portNptNoVirtualFunctionsAvailable
    
        At least some of the physical NICs used as uplinks for this port support VMDirectPath Gen 2, but all available network-passthrough resources are in use by other ports.
        
    

from pyvisdk.do.host_event import HostEvent
import logging

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

class HostCnxFailedNoConnectionEvent(HostEvent):
    '''This event records a failure to connect to a host due to a host not being present
        on the network.
    '''
    
    def __init__(self, ):
        # MUST define these
        super(HostCnxFailedNoConnectionEvent, self).__init__()
    

    
    
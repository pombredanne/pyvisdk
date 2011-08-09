
from pyvisdk.mo.consts import ManagedEntityTypes
from pyvisdk.mo.base_entity import BaseEntity
import logging

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

class IpPoolManager(BaseEntity):
    '''Singleton Managed Object used to manage IP Pools.IP Pools are used to allocate
        IPv4 and IPv6 addresses to vApps.
    '''
    def __init__(self, core, name=None, ref=None, type=ManagedEntityTypes.IpPoolManager):
        # MUST define these
        super(IpPoolManager, self).__init__(core, name=name, ref=ref, type=type)
    
    

    def CreateIpPool(self, dc, pool):
        '''Create a new IP pool.The name field must be defined, all other fields are
        optional. If unset, they will be given default values.The ID for the pool
        is generated by the server and should not be defined on the pool object
        passed to this method.

        :param dc: to a DatacenterThe datacenter on which to create the pool.

        :param pool: The IP pool to create on the server


        :rtype: xsd:int 

        '''
        
        return self.delegate("CreateIpPool")(dc,pool)
        

    def DestroyIpPool(self, dc, id, force):
        '''Destroys an IP pool on the given datacenter.Looks up the pool on the datacenter by
        ID and deletes it. If the pool is in use, the method throws InvalidState
        unless the force flag is true.

        :param dc: to a DatacenterThe datacenter on which to find the pool

        :param id: The unique ID of the pool

        :param force: If true, the pool will be destroyed even if it is in use

        '''
        
        return self.delegate("DestroyIpPool")(dc,id,force)
        

    def QueryIpPools(self, dc):
        '''Return the list of IP pools for a datacenter.

        :param dc: to a DatacenterThe datacenter for which to look up the IP pools.


        :rtype: IpPool[] 

        '''
        
        return self.delegate("QueryIpPools")(dc)
        

    def UpdateIpPool(self, dc, pool):
        '''Update an IP pool on a datacenter.The pool to update is looked up from the value
        of the id field.All fields in the pool except the id are optional. Only
        defined values are stored on the server.

        :param dc: to a DatacenterThe datacenter on which to look up the pool.

        :param pool: The IP pool to update on the server

        '''
        
        return self.delegate("UpdateIpPool")(dc,pool)
        
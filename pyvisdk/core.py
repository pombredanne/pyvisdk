'''
Created on Feb 15, 2011

@author: eplaster
'''
from pyvisdk.client import Client
from pyvisdk.base.managed_object_types import ManagedObjectTypes
from pyvisdk.base.base_entity import ManagedObjectReference
from pyvisdk.consts import TaskInfoState
from pyvisdk.exceptions import VisdkTaskError
from pyvisdk.mo.service_instance import ServiceInstance
from suds.sudsobject import Property
import logging
import urllib2
import xml.etree.cElementTree as etree

fmt = "[%(asctime)s][%(levelname)-8s] %(module)s.%(funcName)s:%(lineno)d %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class VimBase(object):
    '''
    Base class to hold the nuts and bolts for the web services grunt work.
    '''


    def __init__(self, server, connect=True, verbose=3):
        '''
        Constructor
        '''
        self.server = server
        self.verbose = verbose
        self.connected = False
        
        self.listeners = {}
        for me in ManagedObjectTypes:
            self.listeners[me] = []
         
        # setup logging...
        logging.getLogger('suds.client').setLevel(logging.INFO)
        logging.getLogger('suds.wsdl').setLevel(logging.INFO)
        logging.getLogger('suds.transport').setLevel(logging.INFO)
        logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
       
        if self.verbose > 5:
            logging.getLogger('suds.client').setLevel(logging.DEBUG)
            logging.getLogger('suds.transport').setLevel(logging.DEBUG)
        
        if connect:
            self.connect()
        
    def connect(self, timeout=1800):
        if self.connected:
            return
        
        self.client = Client(self.server, timeout=timeout)
        
        # create the Service Instance managed object
        ref = Property('ServiceInstance')
        ref._type = 'ServiceInstance'
        self.service_instance = ServiceInstance(self, name='ServiceInstance', ref=ref)

        # get the service content
        #self.service_content = self.client.RetrieveServiceContent(self.service_instance)
        self.service_content = self.service_instance.RetrieveServiceContent()
        self.property_collector = self.service_content.propertyCollector

        self.root = self.service_content.rootFolder
        self.connected = True
    
    def getVersions(self):
        versions = []
        
        def get_namespace_name(elem):
            for child in list(elem):
                if child.tag == "name":
                    return child.text
            
        url = urllib2.urlopen("https://"+self.server+"/sdk/vimServiceVersions.xml")
        root = etree.fromstring(url.read())
        names = root.findall(".//namespace")
        for namesp in names:
            if "urn:vim25" in get_namespace_name(namesp):
                versions = [x.text for x in namesp.findall(".//version")]
                log.debug("versions found: " + str(versions))
        return versions
        
    def callRetrievePropertiesEx(self, maxObjects=0):
        myPropSpec = self.PropertySpec(all=False, _type=ManagedObjectTypes.VirtualMachine, pathSet=["name"])
       
        myObjSpec = self.ObjectSpec(self.root, selectSet=self.buildFullTraversal())
       
        pSpec = self.PropertyFilterSpec(propSet=[myPropSpec], objectSet=[myObjSpec])
       
        rOptions = self.RetrieveOptions(int(maxObjects))
      
        retrieveResult = self.client.RetrievePropertiesEx([self.property_collector], [pSpec], rOptions)      
      
        #objContentArrayList = Arrays.asList(retrieveResult.getObjects())
        #if(retrieveResult.getToken() != null && maxObjects == null) {
        #   callContinueRetrieveProperties(retrieveResult.getToken())
        #}            
        #ObjectContent [] objectContentArray = (ObjectContent [])objContentArrayList.toArray()
        #for(int i=0; i<objectContentArray.length; i++) {
        #   System.out.println("VM Managed Object Reference Value: " + objectContentArray[i].getObj().get_value());
        #}
        return retrieveResult

    def getObjectProperties(self, mobj, properties, collector=None):
        """
        * Retrieve contents for a single object based on the property collector
        * registered with the service.
        *
        * @param collector Property collector registered with service
        * @param mobj Managed Object Reference to get contents for
        * @param properties names of properties of object to retrieve
        *
        * @return retrieved object contents
        """
        if not collector:
            collector = self.property_collector
        
        all = False
        if not properties:
            all = True
        
        pspec = self.PropertySpec(all=all, _type=mobj._type, pathSet=properties)
        ospec = self.ObjectSpec(obj=ManagedObjectReference(mobj._type, mobj.value), skip=False)
        spec = self.PropertyFilterSpec(propSet=[pspec], objectSet=[ospec])
        
        return self.client.RetrieveProperties(collector, [spec])


    def getDynamicProperty(self, mo, property):
        log.debug("Getting properties for: %s" % property)
        value = None
        objContent = self.getObjectProperties(mo, [property])
        rv = {}
        if objContent:
            if hasattr(objContent[0], 'propSet'):
                props = objContent[0].propSet
                for prop in props:
                    value = prop.val
                    name = value.__class__.__name__
                    if "ArrayOf" in name:
                        methodname = name[7:]
                        
                        # special cases...
                        if methodname == 'String':
                            methodname = 'string'
                            
                        value = eval("value.%s" % methodname)
                    rv[prop.name] = value
        return rv
    

    def getDecendentsByName(self, _type, properties=["name"], name=None, root=None):
        """
         * Get the ManagedObjectReference for an item under the specified root
         * folder that has the type and name specified.
         * 
         * @param _type
         *            type of the managed object
         * @param properties 
         *            names of properties of object to retrieve
         * @param name
         *            name to match
         * @param root
         *            a root folder if available, or null for default
         * 
         * @return First ManagedObjectReference of the type / name pair found
        """
        if not "name" in properties:
            properties += ["name"]
        ocary = self.getContentsRecursively(_type=str(_type), props=properties, root=root)
        log.debug("ocary: %s" % ocary)

        if ocary:
            if not name:
                return ocary
            
            for vm in ocary:
                found = False
                if vm.propSet:
                    for prop in vm.propSet:
                        if prop.name == "name" and prop.val == name:
                            found = True
                            break
                if found:
                    return vm

    def getContentsRecursively(self, props=[], _type=None, collector=None, root=None, recurse=True):
        if not collector: collector = self.property_collector
        if not root: root = self.root
        if not _type: _type = ManagedObjectTypes.ManagedEntity
            
        typeinfo = [ self.PropertySpec(_type=str(_type), pathSet=props) ]

        selectionSpecs = []
        if recurse:
            selectionSpecs = self.buildFullTraversal()
         
        spec = self.PropertyFilterSpec(propSet=typeinfo, objectSet=[ self.ObjectSpec(root, selectSet=selectionSpecs) ])
        return self.client.RetrieveProperties(collector, [ spec ])
    
    def collectProperties(self):
        pass
        
   
    def buildFullTraversal(self):
        """
         * This method creates a SelectionSpec[] to traverses the entire inventory
         * tree starting at a Folder
         * 
         * @return The SelectionSpec[]
        """
        # Recurse through all ResourcePools
        rpToRp = self.TraversalSpec(name="rpToRp", _type=ManagedObjectTypes.ResourcePool, path="resourcePool",
                        selectSet=[ self.SelectionSpec("rpToRp"), self.SelectionSpec("rpToVm") ])

        # Recurse through all ResourcePools
        rpToVm = self.TraversalSpec(name="rpToVm", _type=ManagedObjectTypes.ResourcePool, path="vm")

        # Traversal through ResourcePool branch
        crToRp = self.TraversalSpec(name="crToRp", _type=ManagedObjectTypes.ComputeResource, path="resourcePool",
                        selectSet=[ self.SelectionSpec("rpToRp"), self.SelectionSpec("rpToVm") ])

        # Traversal through host branch
        crToH = self.TraversalSpec(name="crToH", _type=ManagedObjectTypes.ComputeResource, path="host")
        
        # Traversal through hostFolder branch
        dcToHf = self.TraversalSpec(name="dcToHf", _type=ManagedObjectTypes.Datacenter, path="hostFolder",
                        selectSet=[self.SelectionSpec("visitFolders")])

        # Traversal through vmFolder branch
        dcToVmf = self.TraversalSpec(name="dcToVmf", _type=ManagedObjectTypes.Datacenter, path="vmFolder",
                        selectSet=[self.SelectionSpec("visitFolders")])

        # Recurse through all Hosts
        HToVm = self.TraversalSpec(name="HToVm", _type=ManagedObjectTypes.HostSystem, path="vm",
                        selectSet=[self.SelectionSpec("visitFolders")])
        
        # Recurse through the folders
        visitFolders = self.TraversalSpec(name="visitFolders", _type=ManagedObjectTypes.Folder, path="childEntity",
                        selectSet=[ self.SelectionSpec("visitFolders"),
                                     self.SelectionSpec("dcToHf"),
                                     self.SelectionSpec("dcToVmf"),
                                     self.SelectionSpec("crToH"),
                                     self.SelectionSpec("crToRp"),
                                     self.SelectionSpec("HToVm"),
                                     self.SelectionSpec("rpToVm"), ])
        
        return (visitFolders, dcToVmf, dcToHf, crToH, crToRp, rpToRp, HToVm, rpToVm)
 
    """
    * Illustrating how to create, use and destroy additional property collectors
    * This allows multiple modules to create their own property filter and process updates independently.
    * Also applow to get time-sensitive updated being monitored on one collector, 
    * while a large updatyed being monitored by another.
    """
    def callCreatePropertyCollectorEx(self):
        propCol = self.client.CreatePropertyCollector(self.property_collector)
        collector = ManagedObjectReference(ManagedObjectTypes.PropertyCollector, propCol.value)
        
        if self.verbose > 5:
            log.debug(str(collector))
      
        pSpec = self.PropertyFilterSpec(
                propSet=[
                    self.PropertySpec(_type=ManagedObjectTypes.VirtualMachine, all=False, pathSet=["configIssue", "configStatus", "name", "parent"])
                ],
                objectSet=[
                    self.ObjectSpec(self.root, selectSet=self.buildFullTraversal())
                ])
         
        rOptions = self.RetrieveOptions()
        
        retrieveResult = self.client.RetrievePropertiesEx(collector, pSpec, rOptions)      
        self.client.DestroyPropertyCollector(collector)
        return retrieveResult
    
    def _parseTaskResponse(self, response):
        status = {}
        for x in response.filterSet[0].objectSet[0].changeSet:
            if hasattr(x, 'val'):
                status[x.name] = x.val
            else:
                status[x.name] = x.op
        return status

    def waitForTask(self, objmor):
        version = ""

        objmor = ManagedObjectReference("Task", objmor.value)

        myObjSpec = self.ObjectSpec(objmor)
        myPropSpec = self.PropertySpec(_type=objmor._type, pathSet=["info.state", "info.error"])
        pSpec = self.PropertyFilterSpec(propSet=[myPropSpec], objectSet=[myObjSpec])

        filterSpecRef = self.client.CreateFilter(self.property_collector, pSpec, True)
        filterSpecRef = ManagedObjectReference("PropertyFilter", filterSpecRef.value)
        
        
        updateset = self.client.WaitForUpdates(self.property_collector, version)
        
        status = self._parseTaskResponse(updateset)
        while status['info.state'] == TaskInfoState.running or status['info.state'] == TaskInfoState.queued:
            log.debug("Waiting for task to complete...")
            
            version = updateset.version
            updateset = self.client.WaitForUpdates(self.property_collector, version)
            status = self._parseTaskResponse(updateset)
            log.debug("**** status: %s" % status)
        
        log.debug("Finished task...")
        # Destroy the filter when we are done.
        self.client.DestroyPropertyFilter(filterSpecRef)
        
        if status['info.state'] == TaskInfoState.error:
            error = status['info.error']
            raise VisdkTaskError(error.localizedMessage)
        return status['info.state']

    def update(self, _type="", root=None, properties=[], version="", wait_time=2):
        if not root: root = self.root
        
        myObjSpec = self.ObjectSpec(root)
        myPropSpec = self.PropertySpec(_type=_type, pathSet=properties)
        pSpec = self.PropertyFilterSpec(propSet=[myPropSpec], objectSet=[myObjSpec])

        filterSpecRef = self.client.CreateFilter(self.property_collector, pSpec, False)
        filterSpecRef = ManagedObjectReference("PropertyFilter", filterSpecRef.value)
        
        log.debug("Calling CheckForUpdates with version: %s" % version)
        changeData = self.client.CheckForUpdates(self.property_collector, version)
        
        log.debug("Finished update...")
        # Destroy the filter when we are done.
        self.client.DestroyPropertyFilter(filterSpecRef)
        
        if hasattr(changeData, "filterSet"):
            changeData = changeData.filterSet[0].objectSet[0]
            
        if hasattr(changeData, "changeSet"):
            changeData = changeData.changeSet
            
        return changeData, version
        
    """ Factory Objects """
    def RetrieveOptions(self, maxObjects=0):
        spec = self.client.factory.create('ns0:RetrieveOptions')
        if int(maxObjects):
            spec.maxObjects = int(maxObjects)
        return spec
        
    # ObjectSpec factory
    def ObjectSpec(self, obj, skip=False, selectSet=[]):
        """
        Identifies the starting object for property collection. An ObjectSpec also identifies 
          additional objects for collection.
        """
        spec = self.client.factory.create('ns0:ObjectSpec')
        spec.obj = obj
        spec.skip = skip
        if selectSet:
            spec.selectSet = selectSet
        return spec
    
    # TraversalSpec factory
    def TraversalSpec(self, name, _type, path, skip=False, selectSet=[]):
        """
        Identifies the type of object for property collection. It also provides one or more paths 
              for inventory traversal.
        """
        spec = self.client.factory.create('ns0:TraversalSpec')
        spec.name = name
        spec.path = path
        spec.type = _type
        spec.skip = skip
        if selectSet:
            spec.selectSet = selectSet
        return spec

    # PropertySpec factory
    def PropertySpec(self, _type, all=False, pathSet=[]):
        """
        Identifies properties for collection.
        """
        spec = self.client.factory.create('ns0:PropertySpec')
        spec.type = _type
        spec.all = all
        spec.pathSet = pathSet
        return spec

    # PropertyFilterSpec factory
    def PropertyFilterSpec(self, propSet=[], objectSet=[]):
        """
        Provides access to object and property selection data. A PropertyFilterSpec must 
          have at least one ObjectSpec and one PropertySpec
        """
        spec = self.client.factory.create('ns0:PropertyFilterSpec')
        spec.objectSet = objectSet
        spec.propSet = propSet
        spec.reportMissingObjectsInResults = True
        return spec

    # SelectionSpec factory
    def SelectionSpec(self, name):
        """
        Acts as a placeholder reference to a TraversalSpec.
        """
        spec = self.client.factory.create('ns0:SelectionSpec')
        spec.name = name
        return spec

        
        
        
        
        
        
    
    

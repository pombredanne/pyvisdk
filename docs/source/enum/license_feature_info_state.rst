
==================================================================================================
LicenseFeatureInfoState
==================================================================================================

.. describe:: LicenseFeatureInfoState

    Describes the state of the feature.
    
    
    .. py:data:: LicenseFeatureInfoState.disabled
    
        The current edition license does not allow this additional feature.
        
    
    .. py:data:: LicenseFeatureInfoState.enabled
    
        The current edition license has implicitly enabled this additional feature.
        
    
    .. py:data:: LicenseFeatureInfoState.optional
    
        The current edition license allows this additional feature. The EnableFeature and DisableFeature methods can be used to enable or disable this feature.
        
    
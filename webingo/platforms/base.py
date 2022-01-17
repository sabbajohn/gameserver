class PlatformBase:
    
    def name(self):
        raise NotImplementedError("platform has no name")
    
    def get_components( self, controller ):
        return {}

    async def get_registry(self, site, uid, ip_addr):
        raise NotImplementedError("unimplemented get_registry")

    def get_user( self ):
        raise NotImplementedError("unimplemented get_user")

from .demo import PlatformDemo, PortalDemo
from .fb import PlatformFacebook, PortalFacebook
from .fb_web import FacebookWeb

def create_platform_broker( name, auth_data, site ):
    if(name == "demo"):
        return PlatformDemo(auth_data, site)
    elif(name == "facebook"):
        return PlatformFacebook(auth_data, site)
    else:
        raise Exception("Unknown platform: "+name)


def register_platform_http_handlers( app ):
    PortalDemo.register( app )
    PortalFacebook.register( app )
    FacebookWeb.register(app)

"""Module containing a template for a main service."""

import logging
import sys
import Ice

try:
    import IceFlix

except ImportError:
    import os
    Ice.loadSlice(os.path.join(os.path.dirname(__file__), "iceflix.ice"))
    import IceFlix



class Main(IceFlix.Main):
    """Servant for the IceFlix.Main interface.
    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """

    def getAuthenticator(self, current):  # pylint:disable=invalid-name, unused-argument
        "Return the stored Authenticator proxy."
        # TODO: implement
        return None

    def getCatalog(self, current):  # pylint:disable=invalid-name, unused-argument
        "Return the stored MediaCatalog proxy."
        # TODO: implement
        return None

    def newService(self, proxy, service_id, current):  # pylint:disable=invalid-name, unused-argument
        "Receive a proxy of a new service."
        print("Recibido mensaje NEWSERVICE()")
        authenticator = IceFlix.AuthenticatorPrx.checkedCast(proxy)
        
        try:
            authenticator.addUser("hola","adios","1234")
            #authenticator.removeUser("EnriqueAP6","1234")
            tokenUsuario = authenticator.refreshAuthorization("hola","adios")
            #print("¿ESTÁ AUTORIZADO EL USUARIO CON EL TOKEN 1234EW3 ? --> " + str(authenticator.isAuthorized("1234EW3")))
            print(f"¿ESTÁ AUTORIZADO EL USUARIO CON EL TOKEN {tokenUsuario}? --> " + str(authenticator.isAuthorized(tokenUsuario)))
            print("¿ES ADMIN EL USUARIO CON EL TOKEN 1234 ? --> " + str(authenticator.isAdmin("1234")))
            print(f"¿ES ADMIN EL USUARIO CON EL TOKEN {tokenUsuario}? --> " + str(authenticator.isAdmin(tokenUsuario)))
            #print("¿QUIÉN ES EL USUARIO CON EL TOKEN 1234EW3? --> " + authenticator.whois("1234EW3"))
            print(f"¿QUIÉN ES EL USUARIO CON EL TOKEN {tokenUsuario}? --> " + authenticator.whois(tokenUsuario))
        except IceFlix.TemporaryUnavailable:
            print("\n\nTEMPORARY UNAVALIABLE")
        except IceFlix.Unauthorized:
            print("\n\nUNAUTHORIZED")


        return

    def announce(self, proxy, service_id, current):  # pylint:disable=invalid-name, unused-argument
        "Announcements handler."
        print("Recibido mensaje ANNOUNCE()")
        return


class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""

    def __init__(self):
        super().__init__()
        self.servant = Main()
        self.proxy = None
        self.adapter = None

    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""
        logging.info("Running Main application")
        broker = self.communicator()
       

        self.adapter = broker.createObjectAdapterWithEndpoints("MainAdapter","tcp")
        proxy = self.adapter.add(self.servant, broker.stringToIdentity("Main"))
        #self.proxy = self.adapter.addWithUUID(self.servant)

        print(proxy, flush=True)
       
        self.adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


s = MainApp()
sys.exit(s.main(sys.argv))
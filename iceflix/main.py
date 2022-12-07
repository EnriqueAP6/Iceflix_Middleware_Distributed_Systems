"""Module containing a template for a main service."""

import logging
import sys
import Ice
from time import sleep
import hashlib

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

    def getsha256cadena(self,cadena):
      hashsha  = hashlib.sha256()
      hashsha.update(cadena.encode())
      return hashsha.hexdigest() 

    def newService(self, proxy, service_id, current):  # pylint:disable=invalid-name, unused-argument
        "Receive a proxy of a new service."
        print("Recibido mensaje NEWSERVICE()")
        authenticator = IceFlix.AuthenticatorPrx.checkedCast(proxy)
        
        try:
            print("Añadiendo usuario nuevo")
            authenticator.addUser("hola",self.getsha256cadena("adios"),"1234")  #usuario nuevo
            print("Añadiendo usuario registrado")
            #authenticator.addUser("EnriqueAP6",self.getsha256cadena("dsvfd "),"1234")  #usuario ya registrado
            sleep(3)
            print("Añadiendo usuario nuevo")
            authenticator.addUser("Enri",self.getsha256cadena("adios"),"1234")  #usuario nuevo
            print("Eliminado usuario existente")
            authenticator.removeUser("Enri","1234") #borrado usuario existente
            print("Eliminando usuario inexistente")
            authenticator.removeUser("djfvdb ","1234") #borrado usuario inexistente
            print("Pidiendo token nuevo")
            tokenUsuario = authenticator.refreshAuthorization("hola",self.getsha256cadena("adios")) #usuario existente
            #print("¿ESTÁ AUTORIZADO EL USUARIO CON EL TOKEN 1234EW3 ? --> " + str(authenticator.isAuthorized("1234EW3"))) #usuario inexistente
            print(f"¿ESTÁ AUTORIZADO EL USUARIO CON EL TOKEN {tokenUsuario}? --> " + str(authenticator.isAuthorized(tokenUsuario))) #usuario existente
            print("¿ES ADMIN EL USUARIO CON EL TOKEN 1234 ? --> " + str(authenticator.isAdmin("1234"))) #administrador
            print(f"¿ES ADMIN EL USUARIO CON EL TOKEN {tokenUsuario}? --> " + str(authenticator.isAdmin(tokenUsuario))) #no administrador
            #print("¿QUIÉN ES EL USUARIO CON EL TOKEN 1234EW3? --> " + authenticator.whois("1234EW3")) #usuario inexistente
            print(f"¿QUIÉN ES EL USUARIO CON EL TOKEN {tokenUsuario}? --> " + authenticator.whois(tokenUsuario)) #usuario existente
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
        self.proxy = self.adapter.addWithUUID(self.servant)

        print(self.proxy, flush=True)
       
        self.adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


s = MainApp()
sys.exit(s.main(sys.argv))
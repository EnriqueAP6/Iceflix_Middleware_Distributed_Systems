"""Módulo con el código destinado al servicio de autenticación."""

import logging

import Ice

import IceFlix  # pylint:disable=import-error


class Authenticator(IceFlix.Authenticator):
    """Sirviente para la interfaz IceFlix.Authenticator"""

    def refreshAuthorization(self, user, passwordHash):  # pylint:disable=invalid-name, unused-argument
        "Crea un nuevo token de autorización de usuario si las credenciales son válidas."
        # TODO: implement
        return None

    def isAuthorized(self, userToken):  # pylint:disable=invalid-name, unused-argument
        "Indica si un token dado es válido o no."
        # TODO: implement
        return None

    def whois(self, userToken):  # pylint:disable=invalid-name, unused-argument
        "Permite descubrir el nombre del usuario a partir de un token válido."
        # TODO: implement
        return

    def isAdmin(self, adminToken):  # pylint:disable=invalid-name, unused-argument
        "Devuelve un valor booleano para comprobar si el token proporcionado corresponde o no con el administrativo."
        # TODO: implement
        return
    
    def addUser(self, user, passwordHash, adminToken):  # pylint:disable=invalid-name, unused-argument
        "Función administrativa que permite añadir unas nuevas credenciales en el almacén de datos si el token administrativo es correcto."
        # TODO: implement
        return
    
    def removeUser(self, user, adminToken):  # pylint:disable=invalid-name, unused-argument
        "Función administrativa que permite eliminar unas credenciales del almacén de datos si el token administrativo es correcto."
        # TODO: implement
        return


class AuthenticatorApp(Ice.Application):
    """Ice.Application para el servicio Authenticator."""

    def __init__(self):
        super().__init__()
        self.servant = Authenticator()
        self.proxy = None
        self.adapter = None

    def run(self, args):
        """Ejecuta la aplicación, añadiendo los objetos necesarios al adaptador."""
        logging.info("Running Authenticator application")
        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        self.adapter.activate()

        self.proxy = self.adapter.addWithUUID(self.servant)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()

        return 0
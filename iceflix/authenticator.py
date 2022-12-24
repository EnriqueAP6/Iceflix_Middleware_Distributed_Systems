"""Módulo con el código destinado al servicio de autenticación."""

import logging
import time
import threading
import uuid
import os
#import sys
import Ice # pylint:disable=import-error

try:
    import IceFlix
    import IceStorm

except ImportError:
    Ice.loadSlice(os.path.join(os.path.dirname(__file__), "iceflix.ice"))
    import IceFlix
    import IceStorm


registro_authenticators = {}
registro_mains = {}

class AuthenticatorAnnouncements(IceFlix.Announcement):
    
    def __init__(self,service_id):

        self.id_authenticator = service_id
        self.candadoregistroauthenticators = threading.Lock()
        self.candadoregistromains = threading.Lock()
    
    def announce(self, service, serviceId, current: Ice.Current=None):
        print("¡¡¡Recibido un announce!!!") #quitar luego
       
        if (service.ice_isA('::IceFlix::Main') and not self.compruebaserviceidsauthenticators(serviceId,registro_mains,self.candadoregistromains)):
            print("Recibido desde un Main el serviceId: " + serviceId)
            with self.candadoregistromains:
                registro_mains[serviceId] = service

        if (service.ice_isA('::IceFlix::Authenticator') and serviceId != self.id_authenticator and not self.compruebaserviceidsauthenticators(serviceId,registro_authenticators,self.candadoregistroauthenticators)):
            print("Recibido desde un Authenticator el serviceId: " + serviceId)
            with self.candadoregistroauthenticators:
                registro_authenticators[serviceId] = service



    def compruebaserviceidsauthenticators(self, service_id, diccionario, candado):
        
        idexistente = False

        with candado:
            for valor in diccionario.values():
                    if service_id == valor[0]:
                        idexistente = True
                        break

        return idexistente

    def anunciarperiodicamente(self,publicador_subscriptor,proxy_authenticator,tiempo_announce):
        while True:
            print(registro_authenticators)
            print(registro_mains)
            print("Va a anunciarse el authenticator")
            publicador_subscriptor.announce(proxy_authenticator,self.id_authenticator)
            time.sleep(tiempo_announce)



class Authenticator(IceFlix.Authenticator):
    """Sirviente para la interfaz IceFlix.Authenticator"""

    def __init__(self, tokenadministracion, tiempovalideztokens, nombrearchivo):
        self.contadortokenscreados = 0
        self.tiempovalideztokens= tiempovalideztokens
        # los 2 minutos durante los cuales los token mantienen su validez
        self.diccionariotokens = {}
        #se guardará el token y el tiempo de vigencia para cada usuario
        self.nombrearchivo = nombrearchivo
        #operación necesaria para inicializar el fichero
        #en caso de no existir previamente
        basedatos = open(self.nombrearchivo,"a", encoding="utf-8") # pylint:disable=R1732
        basedatos.close()
        self.tokenadministracion = tokenadministracion
        #necesitará una serie de candados
        self.candadoarchivotexto = threading.Lock()
        self.candadolistatokens = threading.Lock()

    def envejecelista(self):
        """Controla la validez de los token con el paso del tiempo"""

        while True:

            with self.candadolistatokens:
                #controlo la lista temporal con sección crítica

                diccionarioaux = self.diccionariotokens.copy()

                for entrada in diccionarioaux:
                    if (self.diccionariotokens[entrada][1] + 1) == self.tiempovalideztokens:
                        print((f"Eliminada la entrada:{self.diccionariotokens.pop(entrada)}\n"))
                    else:
                        self.diccionariotokens[entrada][1] += 1

            time.sleep(1)

    def asociausuariotoken(self, user):
        """Inserta en la lista de token a un usuario junto con un """
        """token nuevo que no se repetirá""" # pylint:disable=W0105

        with self.candadolistatokens:
            #controlo la lista temporal con sección crítica

            tokenusuario = "token" + str(self.contadortokenscreados)
            # esta numeración no podrá repetirse
            #durante una ejecución (y cuando acabe se borrarán todos los datos)
            self.contadortokenscreados += 1

            #se controla el caso de renovar el token de un usuario borrado de la lista temporal por
            # tiempo expirado (pero siga en la BD)
            # también se controla el caso de que el sistema esté recién iniciado y la lista temporal
            # vacía
            print(f"Añadida la entrada: {[tokenusuario,0]}\n")
            self.diccionariotokens[user] = [tokenusuario,0]

        return tokenusuario

    def compruebacredenciales(self, user, password):
        """Verifica que un usuario y contraseña estén en el """
        """arhivo de texto usado como base de datos""" # pylint:disable=W0105
        credencialesvalidas = False

        with self.candadoarchivotexto:
            #controlo el archivo persistente con sección crítica

            with  open(self.nombrearchivo,"r",encoding="utf-8") as archivoleer:
                lineasleidas = archivoleer.readlines()
                archivoleer.close()

            for numlinea in range(len(lineasleidas)): # pylint:disable=C0200
                if user == lineasleidas[numlinea][len("[USUARIO] "):-1]:
                    if password == lineasleidas[numlinea+1][len("[CONTRASEÑA] "):-1]:
                    #primera condición evita que falle porque la última contraseña sea igual al
                    # nombre del usuario buscado
                    #tercera condición permite comprobar si un usuario ya está registrado
                    # en la base de datos
                        credencialesvalidas = True

        return credencialesvalidas

    def buscauserarchivo(self, user):
        """Devuelve la línea en la que está escrito, dentro del archivo"""
        """ de texto que se usa como base de datos, el nombre de un usuario buscado""" # pylint:disable=W0105

        with self.candadoarchivotexto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombrearchivo,"r", encoding="utf-8") as archivoleer:
                lineasleidas = archivoleer.readlines()
                archivoleer.close()

            for numlinea in range(len(lineasleidas)): # pylint:disable=C0200
                if user == lineasleidas[numlinea][len("[USUARIO] "):-1]:
                    #[:-1] para quitar el salto de línea
                    return numlinea

        #elimina los errores que pudieran producirse si se intenta eliminar
        # un user que no existe
        return -1

    def insertacredencialesarchivo(self, user, password):
        '''Añade a la base de datos el usuario y contraseña pasados como parámetros'''

        with self.candadoarchivotexto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombrearchivo,"a", encoding="utf-8") as archivoescribir:
                archivoescribir.write("\n")
                archivoescribir.write("[USUARIO] "+ user+"\n")
                archivoescribir.write("[CONTRASEÑA] " + password+"\n")
                archivoescribir.close()
            print(f"Añadidas las credenciales de: {user}")

    def eliminalineasarchivo(self, numlinea):
        """Reescribe el contenido del archivo de texto usado como"""
        """base de datos saltándose ciertsa líneas""" # pylint:disable=W0105

        with self.candadoarchivotexto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombrearchivo,"r", encoding="utf-8") as archivoleer:
                lineasleidas = archivoleer.readlines()
                archivoleer.close()

            with open(self.nombrearchivo,"w", encoding="utf-8") as archivoleer:

                for i in range(len(lineasleidas)): # pylint:disable=C0200
                    if i not in [numlinea,numlinea + 1]: #se salta las líneas que contienen
                    #las credenciales a borrar
                        archivoleer.write(lineasleidas[i]) #ahora no añado el salto de línea porque
                        #dejaría una línea en blanco entre datos
                archivoleer.close()


    def refreshAuthorization(self, user, passwordHash, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Crea un nuevo token de autorización de usuario si las credenciales son válidas."
        if self.compruebacredenciales(user, passwordHash): # pylint:disable=R1705
        #pongo True para que tenga en cuenta
        #usuario y contraseña en la comprobación
            print("Solicitado un refresco del token de: " + user)
            tokennuevo = self.asociausuariotoken(user)
            return tokennuevo
        else:
            raise IceFlix.Unauthorized

    def isAuthorized(self, userToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Indica si un token dado es válido o no."
        tokenvalido = False

        with self.candadolistatokens:
            #controlo la lista temporal con sección crítica

            for valor in self.diccionariotokens.values():
                if userToken == valor[0]:
                    tokenvalido = True
                    break

        return tokenvalido

    def whois(self, userToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member, R1710
        "Permite descubrir el nombre del usuario a partir de un token válido."

        if self.isAuthorized(userToken):

            with self.candadolistatokens:
            #controlo la lista temporal con sección crítica

                for entrada in self.diccionariotokens: # pylint:disable=C0206
                    if userToken == self.diccionariotokens[entrada][0]:
                        return entrada

        else:
            raise IceFlix.Unauthorized

    def isAdmin(self, adminToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Devuelve un valor booleano para comprobar si el token proporcionado"
        "corresponde o no con el administrativo." # pylint:disable=W0105
        if adminToken == self.tokenadministracion: # pylint:disable=R1705, R1703
            return True
        else:
            return False

    def addUser(self, user, passwordHash, adminToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Función administrativa que permite añadir unas nuevas credenciales en el almacén de datos"
        "si el token administrativo es correcto." # pylint:disable=W0105
        if self.isAdmin(adminToken):

            if self.buscauserarchivo(user) == -1 :
            #controla el caso de querer registrar un usuario que ya existe
            #(basta con que el nombre del usuario esté en la BD)
                self.insertacredencialesarchivo(user,passwordHash)

                #hay que introducir al user tanto en el archivo como en la lista temporal

                #le asigno un token válido y se pone su timpo de vigencia a 0
                self.asociausuariotoken(user)
            else:
                #si se intenta añadir un usuario que ya existía
                raise IceFlix.Unauthorized

        else:
            raise IceFlix.Unauthorized

    def removeUser(self, user, adminToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Función administrativa que permite eliminar unas credenciales del almacén de"
        "datos si el token administrativo es correcto." # pylint:disable=W0105
        if self.isAdmin(adminToken):

            posicionuserarchivo = self.buscauserarchivo(user)

            if  posicionuserarchivo != -1: #controla el caso de que se intente
            #borrar un user inexistente

                #hay que borrar al user tanto del archivo ...
                self.eliminalineasarchivo(posicionuserarchivo)

                print(f"Eliminadas las credenciales de: {user}")
                #... como de la lista temporal

                with self.candadolistatokens:
                #controlo la lista temporal con sección crítica

                    if user in self.diccionariotokens:
                        print(f"Eliminada la entrada: {self.diccionariotokens.pop(user)}\n")

        else:
            raise IceFlix.Unauthorized


class AuthenticatorApp(Ice.Application):
    """Ice.Application para el servicio Authenticator."""

    def __init__(self):
        super().__init__()
        self.proxy = None
        self.servantauthenticator = None
        self.tiempovalidezservicio = None
        self.service_id = None
        self.hilorenuevaservicio = None
        self.hiloenvejecetokens = None
        self.sirvienteanunciador = None


    def run(self, args):

        """Ejecuta la aplicación, añadiendo los objetos necesarios al adaptador."""

        logging.info("Running Authenticator application")

        #OBTENCIÓN DE LOS DATOS DEL ARCHIVO DE CONFIGURACIÓN
        properties = self.communicator().getProperties()
        tokenadministracion = properties.getProperty("AdminToken")
        tiempovalideztokens = int(properties.getProperty("TimeTokens"))
        self.tiempovalidezservicio = int(properties.getProperty("TimeAnnounce"))
        nombrearchivo = properties.getProperty("BDname")

        self.servantauthenticator = Authenticator(tokenadministracion, tiempovalideztokens, nombrearchivo)

        adapter = (self.communicator()
        .createObjectAdapterWithEndpoints
        ("AuthenticatorAdapter",properties.getProperty("AuthenticatorAdapter.Endpoints")))
        adapter.activate()

        self.proxy = adapter.addWithUUID(self.servantauthenticator)
        self.proxy = IceFlix.AuthenticatorPrx.uncheckedCast(self.proxy)
        print(f'\n\nThe proxy of the authenticator is "{self.proxy}"\n\n')

        self.service_id = str(uuid.uuid4())




        

        #CREACIÓN DE CANALES , PUBLICADORES Y SUBSCRIPTORES
        
        
        topic_manager_str_prx = "IceStorm/TopicManager -t:tcp -h localhost -p 10000"
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
        self.communicator().stringToProxy(topic_manager_str_prx),)

        if not topic_manager:
            raise RuntimeError("Invalid TopicManager proxy")

        topic_name = "Announcements"
        try:
            topic = topic_manager.create(topic_name)
        except IceStorm.TopicExists:
            topic = topic_manager.retrieve(topic_name)


        self.sirvienteanunciador = AuthenticatorAnnouncements(self.service_id)
        proxyAnunciador = adapter.addWithUUID(self.sirvienteanunciador)
        
        qos = {}

        subscriptor_publicador = topic.subscribeAndGetPublisher(qos, proxyAnunciador)
        subscriptor_publicador = IceFlix.AnnouncementPrx.uncheckedCast(subscriptor_publicador)









        self.hiloAnnouncement = threading.Thread(target = self.sirvienteanunciador.anunciarperiodicamente,args=(subscriptor_publicador,self.proxy,self.tiempovalidezservicio,))
        self.hiloAnnouncement.start()

        #hilo para eliminar tokens que han estado activos más del tiempo establecido en el enunciado
        self.hiloenvejecetokens = threading.Thread(target = self.servantauthenticator.envejecelista)
        self.hiloenvejecetokens.start()

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        topic.unsubscribe(proxyAnunciador)

        return 0
import sys
s = AuthenticatorApp()
sys.exit(s.main(sys.argv))

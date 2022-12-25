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
candadoregistroauthenticators = threading.Lock()
candadoregistromains = threading.Lock()

class AuthenticatorAnnouncements(IceFlix.Announcement):
    
    def __init__(self,service_id):

        self.id_authenticator = service_id
    
    def announce(self, service, serviceId, current: Ice.Current=None):
       
        if service.ice_isA('::IceFlix::Main'): 

            with candadoregistromains: 
         
                if self.compruebaserviceids(serviceId,registro_mains):
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Refresco del serviceId de un Main: " + serviceId + "\n")
                else:
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Registro del serviceId de un Main: " + serviceId + "\n")
        
                registro_mains[serviceId] = [service,0]


        elif service.ice_isA('::IceFlix::Authenticator')  and serviceId != self.id_authenticator:
            
            with candadoregistroauthenticators:

                if self.compruebaserviceids(serviceId,registro_authenticators):
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Refresco del serviceId de un Authenticator:  " + serviceId + "\n")
                else:
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Registro del serviceId de un Authenticator:  " + serviceId + "\n")
                registro_authenticators[serviceId] = [service,0]

    def compruebaserviceids(self, service_id, diccionario):
        
        idexistente = False

        for entrada in diccionario:
            if service_id == entrada:
                idexistente = True
                break

        return idexistente

    def anunciarperiodicamente(self,publicador_subscriptor,proxy_authenticator,tiempo_announce):
       
        while True:
            print("[AUTHENTICATOR_ANNOUNCEMENTS] Va a anunciarse el authenticator\n") #quitar luego
            publicador_subscriptor.announce(proxy_authenticator,self.id_authenticator)
            time.sleep(tiempo_announce)

    def envejecediccionario(self,diccionario, candado, tiempo_vigencia):

        while True:

            with candado:
                #controlo la lista temporal con sección crítica

                diccionarioaux = diccionario.copy()

                for entrada in diccionarioaux:
                    if (diccionario[entrada][1]) == tiempo_vigencia:
                        print((f"[AUTHENTICATOR_ANNOUNCEMENTS] Eliminado el serviceId: {diccionario.pop(entrada)}\n"))
                    else:
                        diccionario[entrada][1] += 1
            time.sleep(1)


class AuthenticatorUserUpdates(IceFlix.UserUpdate):

    def __init__(self, referencia_authenticator, tokenadministracion):
        self.referencia_authenticator = referencia_authenticator
        self.tokenadministracion = tokenadministracion #HAY QUE VER CÓMO CAMBIARLO LUEGO #####################################################################33

    def newToken(self, user, token, serviceId, current: Ice.Current=None):
        
        print(f"[AUTHENTICATOR_USERUPDATES] Recibido newToken({user},{token},{serviceId})\n")
        if(self.compruebaserviceidsauthenticators(serviceId,registro_authenticators,candadoregistroauthenticators)):
            self.referencia_authenticator.imponetokenusuario(user, token) 

    def revokeToken(self, token, serviceId, current: Ice.Current=None):
        
        print(f"[AUTHENTICATOR_USERUPDATES] Recibido revokeToken({token},{serviceId})\n")
        if(self.compruebaserviceidsauthenticators(serviceId,registro_authenticators,candadoregistroauthenticators)):
            self.referencia_authenticator.eliminaentradatoken(token)

    def newUser(self, user, passwordHash, serviceId, current: Ice.Current=None):
        
        print(f"[AUTHENTICATOR_USERUPDATES] Recibido newUser({user},{passwordHash},{serviceId})\n")
        if(self.compruebaserviceidsauthenticators(serviceId,registro_authenticators,candadoregistroauthenticators)):
            self.referencia_authenticator.addUser(user, passwordHash, self.tokenadministracion)
    
    def removeUser(self, user, serviceId, current: Ice.Current=None):
        
        print(f"[AUTHENTICATOR_USERUPDATES] Recibido removeUser({user},{serviceId})\n")
        if(self.compruebaserviceidsauthenticators(serviceId,registro_authenticators,candadoregistroauthenticators)):
            self.referencia_authenticator.removeUser(user, self.tokenadministracion)

    def compruebaserviceidsauthenticators(self, service_id, diccionario, candado):
        
        idexistente = False

        with candado:
            for entrada in diccionario:
                    if service_id == entrada:
                        idexistente = True
                        break

        return idexistente


class AuthenticatorData(IceFlix.AuthenticatorData):

    def __init__(self):
        self.adminToken = None
        self.currentUsers = None
        self.activeTokens = None

    def set_admin_token(self, admin_token):
        self.adminToken = admin_token
    
    def set_current_users(self, current_users):
        self.currentUsers = current_users #el argumento será un diccionario
    
    def set_active_tokens(self, active_tokens):
        self.activeTokens = active_tokens #el argumento será un diccionario


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

        self.service_id = None
        self.publicador_userupdates = None

    def setpublicador(self, publicador_userupdates):
        self.publicador_userupdates = publicador_userupdates

    def setserviceid(self, service_id):
        self.service_id = service_id

    def settokenadministracion(self, tokenadministracion):
        self.tokenadministracion = tokenadministracion

    def setdiccionariotokens(self, diccionariotokens):
        with self.candadolistatokens:
            self.diccionariotokens = {}
            for entrada in diccionariotokens:
                self.diccionariotokens[entrada] = [diccionariotokens[entrada],0]

    def setnuevosusuarios(self, diccionariousers):

        with self.candadoarchivotexto:
            with open(self.nombrearchivo,"w", encoding="utf-8") as archivoleer:
                for entrada in diccionariousers:
                    self.insertacredencialesarchivo(entrada,diccionariousers[entrada])

    def envejecelista(self):
        """Controla la validez de los token con el paso del tiempo"""

        while True:

            with self.candadolistatokens:
                #controlo la lista temporal con sección crítica

                diccionarioaux = self.diccionariotokens.copy()

                for entrada in diccionarioaux:
                    if (self.diccionariotokens[entrada][1]) == self.tiempovalideztokens:
                        self.publicador_userupdates.revokeToken(self.diccionariotokens[entrada][0],self.service_id) 
                        print((f"[AUTHENTICATOR] Eliminada la entrada:{self.diccionariotokens.pop(entrada)}\n"))
                    else:
                        self.diccionariotokens[entrada][1] += 1

            time.sleep(1)

    def imponetokenusuario(self, user, token):
       
        with self.candadolistatokens:
            print(f"[AUTHENTICATOR] Añadida/Actualizada la entrada: {[token,0]}\n")
            self.diccionariotokens[user] = [token,0]

    def eliminaentradatoken(self, token):

        with self.candadolistatokens:

            diccionarioaux = self.diccionariotokens.copy()
            for entrada in diccionarioaux:
                if (self.diccionariotokens[entrada][0] == token):
                    print((f"[AUTHENTICATOR] Eliminada la entrada:{self.diccionariotokens.pop(entrada)}\n"))

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
            print(f"[AUTHENTICATOR] Añadida la entrada: {[tokenusuario,0]}\n")
            self.diccionariotokens[user] = [tokenusuario,0]
        
        self.publicador_userupdates.newToken(user, tokenusuario, self.service_id)

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

       
        with open(self.nombrearchivo,"a", encoding="utf-8") as archivoescribir:
            archivoescribir.write("\n")
            archivoescribir.write("[USUARIO] "+ user+"\n")
            archivoescribir.write("[CONTRASEÑA] " + password+"\n")
            archivoescribir.close()
        print(f"[AUTHENTICATOR] Añadidas las credenciales de: {user}\n")

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
            print("[AUTHENTICATOR] Solicitado un refresco del token de: " + user+ "\n")
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
                with self.candadoarchivotexto:
                    self.insertacredencialesarchivo(user,passwordHash)
                    self.publicador_userupdates.newUser(user, passwordHash, self.service_id)
                
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

                print(f"Eliminadas las credenciales de: {user}\n")
                #... como de la lista temporal

                with self.candadolistatokens:
                #controlo la lista temporal con sección crítica

                    if user in self.diccionariotokens:

                        self.publicador_userupdates.removeUser(user, self.service_id)
                        print(f"[AUTHENTICATOR] Eliminada la entrada: {self.diccionariotokens.pop(user)}\n")

        else:
            raise IceFlix.Unauthorized

    def crea_diccionario_active_tokens(self):

        diccionario_envio = {}
        
        with self.candadolistatokens:

            for entrada in self.diccionariotokens:
                diccionario_envio[entrada] = self.diccionariotokens[entrada][0]

        return diccionario_envio

    def crea_diccionario_current_users(self):

        diccionario_envio = {}
        lineasleidas = []
        user = ""
        password = ""

        with self.candadoarchivotexto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombrearchivo,"r", encoding="utf-8") as archivoleer:
                lineasleidas = archivoleer.readlines()
                archivoleer.close()

        for numlinea in range(len(lineasleidas)): # pylint:disable=C0200

                if len("[USUARIO] ") < len(lineasleidas[numlinea]) and lineasleidas[numlinea][:len("[USUARIO] ")] == "[USUARIO] ":
                    user = lineasleidas[numlinea][len("[USUARIO] "):-1]
                    password = lineasleidas[numlinea+1][len("[CONTRASEÑA] "):-1]
                   
                    diccionario_envio[user] = password

        return diccionario_envio
                
    def bulkUpdate(self, current: Ice.Current=None):

        authenticator_data = AuthenticatorData()
        authenticator_data.set_admin_token(self.tokenadministracion)
        authenticator_data.set_current_users(self.crea_diccionario_current_users())
        authenticator_data.set_active_tokens(self.crea_diccionario_active_tokens())

        return authenticator_data


class AuthenticatorApp(Ice.Application):
    """Ice.Application para el servicio Authenticator."""

    def __init__(self):
        super().__init__()
        self.proxy = None
        self.service_id = None
        self.servantauthenticator = None
        self.sirvienteanunciador = None
        self.sirvienteuserupdate = None
        self.hilorenuevaservicio = None
        self.hiloenvejecetokens = None
        self.hiloenvejeceidsauthenticator = None
        self.hiloenvejeceidsmain = None


    def run(self, args):

        """Ejecuta la aplicación, añadiendo los objetos necesarios al adaptador."""

        logging.info("[AUTHENTICATOR_APP] Running Authenticator application")

        #OBTENCIÓN DE LOS DATOS DEL ARCHIVO DE CONFIGURACIÓN
        properties = self.communicator().getProperties()
        tokenadministracion = properties.getProperty("AdminToken")
        tiempovalideztokens = int(properties.getProperty("TimeTokens"))
        tiempovalidezannounce = int(properties.getProperty("TimeAnnounce"))
        tiempovalidezids = int(properties.getProperty("TimeServiceIds"))
        tiempo_arranque = int(properties.getProperty("TimeStart"))

        nombrearchivo = properties.getProperty("BDname")

        self.servantauthenticator = Authenticator(tokenadministracion, tiempovalideztokens, nombrearchivo)

        adapter = (self.communicator()
        .createObjectAdapterWithEndpoints
        ("AuthenticatorAdapter",properties.getProperty("AuthenticatorAdapter.Endpoints")))
        adapter.activate()

        self.proxy = adapter.addWithUUID(self.servantauthenticator)
        print(f'\n\n[AUTHENTICATOR_APP] The proxy of the authenticator is "{self.proxy}"\n\n')
        authenticator = IceFlix.AuthenticatorPrx.uncheckedCast(self.proxy)  #esto ya es la referencia al authenticator

        self.service_id = str(uuid.uuid4())


        

        #CREACIÓN DE CANALES , PUBLICADORES Y SUBSCRIPTORES
        
        
        topic_manager_str_prx = "IceStorm/TopicManager -t:tcp -h localhost -p 10000"
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
        self.communicator().stringToProxy(topic_manager_str_prx),)

        if not topic_manager:
            raise RuntimeError("[AUTHENTICATOR_APP] Invalid TopicManager proxy")

        ############################ Announcements #######################
        topic_name = "Announcements"
        try:
            topic = topic_manager.create(topic_name)
        except IceStorm.TopicExists:
            topic = topic_manager.retrieve(topic_name)


        self.sirvienteanunciador = AuthenticatorAnnouncements(self.service_id)
        proxyanunciador = adapter.addWithUUID(self.sirvienteanunciador)
        
        qos = {}

        subscriptor_publicador_announcements = topic.subscribeAndGetPublisher(qos, proxyanunciador)
        subscriptor_publicador_announcements = IceFlix.AnnouncementPrx.uncheckedCast(subscriptor_publicador_announcements)


        #ALGORITMO DE ARRANQUE

        time.sleep(tiempo_arranque) #esperamos a recibir un anunciamiento de una instancia Main o Authenticator
        with candadoregistromains:
            if (len(registro_mains) == 0): # si no hay ningún Main registrado se corta el programa
                raise RuntimeError("[AUTHENTICATOR_APP] No se ha recibido el anunciamiento de ninguna instancia Main , abortando arranque ...")

        if (len(registro_authenticators) == 0): # si no hay ningún Authenticator registrado se corta el programa
            
            with candadoregistroauthenticators:
                for entrada in registro_authenticators:
                    proxy_authenticator_BD = registro_authenticators[entrada]
                    break
            authenticator_BD = IceFlix.AuthenticatorPrx.uncheckedCast(self.proxy) #poner el proxy del primer authenticator que tengamos
            authenticator_data = authenticator_BD.bulkUpdate()
            
            
            print("############################################################################################")
            print("adminToken: " + authenticator_data.adminToken)
            print("currentUsers: " + str(authenticator_data.currentUsers))
            print("activeTokens: " + str(authenticator_data.activeTokens))
            print("############################################################################################")
            
            self.servantauthenticator.settokenadministracion(authenticator_data.adminToken)
            self.servantauthenticator.setnuevosusuarios(authenticator_data.currentUsers)
            self.servantauthenticator.setdiccionariotokens(authenticator_data.activeTokens)





        ############################# UserUpdates #########################

        topic_name = "UserUpdates"
        try:
            topic = topic_manager.create(topic_name)
        except IceStorm.TopicExists:
            topic = topic_manager.retrieve(topic_name)

        self.sirvienteuserupdate = AuthenticatorUserUpdates(authenticator, tokenadministracion)
        proxyuserupdate = adapter.addWithUUID(self.sirvienteuserupdate)
        
        qos = {}

        subscriptor_publicador_userupdates = topic.subscribeAndGetPublisher(qos, proxyuserupdate)
        subscriptor_publicador_userupdates = IceFlix.UserUpdatePrx.uncheckedCast(subscriptor_publicador_userupdates)

        self.servantauthenticator.setpublicador(subscriptor_publicador_userupdates)
        self.servantauthenticator.setserviceid(self.service_id)



        #HILOS NECESARIOS PARA EL CONTROL DE LA VIGENCIA DE LOS DATOS

        self.hiloAnnouncement = threading.Thread(target = self.sirvienteanunciador.anunciarperiodicamente,args=(subscriptor_publicador_announcements,authenticator,tiempovalidezannounce,))
        self.hiloAnnouncement.start()

        self.hiloenvejeceidsauthenticator = threading.Thread(target = self.sirvienteanunciador.envejecediccionario, args=(registro_authenticators, candadoregistroauthenticators, tiempovalidezids,))
        self.hiloenvejeceidsauthenticator.start()

        self.hiloenvejeceidsmain = threading.Thread(target = self.sirvienteanunciador.envejecediccionario, args=(registro_mains, candadoregistromains, tiempovalidezids,))
        self.hiloenvejeceidsmain.start()

        #hilo para eliminar tokens que han estado activos más del tiempo establecido en el enunciado
        self.hiloenvejecetokens = threading.Thread(target = self.servantauthenticator.envejecelista)
        self.hiloenvejecetokens.start()



        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        topic.unsubscribe(proxyanunciador)
        topic.unsubscribe(proxyuserupdate)

        return 0

#LUEGO QUITAR TODO ESTO #############################################################################################
import sys
s = AuthenticatorApp()
sys.exit(s.main(sys.argv))

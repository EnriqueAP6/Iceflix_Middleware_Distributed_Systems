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
    import IceFlix #pylint:disable=ungrouped-imports
    import IceStorm #pylint:disable=ungrouped-imports


#emplearé un diccionario para guardar los proxys y service_ids de
#instancias Main y otro para las instancias Authenticator
registro_authenticators = {}
registro_mains = {}
#para asegurar la consistencia requeriré del uso de candados
#para cada estructura de datos anteior
candado_registro_authenticators = threading.Lock()
candado_registro_mains = threading.Lock()
#requeriré de dos variables globales extra para arrancar
#el sistema antes de los 12 segundos de espera iniciales
#siempre que ya haya recibido el announce un servicio Main
#y otro de un Authenticator
RECIBIDO_YA_MAIN = False
RECIBIDO_YA_AUTHENTICATOR = False





class AuthenticatorAnnouncements(IceFlix.Announcement):
    """Sirviente para la interfaz IceFlix.Announcement"""

    def __init__(self,service_id):

        self.id_authenticator = service_id


    def announce(self, service, serviceId, current: Ice.Current=None): # pylint:disable=invalid-name, unused-argument, no-member
        '''Guardará los proxy y service_id de instancias Main y Authenticator'''

        global RECIBIDO_YA_AUTHENTICATOR,RECIBIDO_YA_MAIN # pylint:disable=W0603

        if service.ice_isA('::IceFlix::Main'):
            #si el proxy es una instancia Main...

            with candado_registro_mains:

                if self.comprueba_service_ids(serviceId,registro_mains):
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Refresco del serviceId de un Main: "
                    + serviceId + "\n")
                else:
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Registro del serviceId de un Main: "
                    + serviceId + "\n")

                    if not RECIBIDO_YA_MAIN:
                        RECIBIDO_YA_MAIN = True

                registro_mains[serviceId] = [service,0]

        elif service.ice_isA('::IceFlix::Authenticator')  and serviceId != self.id_authenticator:
            #si el proxy es una instancia Authenticator y diferente al mío...

            with candado_registro_authenticators:
                #controlo el diccionario temporal con sección crítica

                if self.comprueba_service_ids(serviceId,registro_authenticators):
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Refresco del serviceId de un" +
                    " Authenticator:  " + serviceId + "\n")
                else:
                    print("[AUTHENTICATOR_ANNOUNCEMENTS] Registro del serviceId de un" +
                    " Authenticator:  " + serviceId + "\n")

                    if not RECIBIDO_YA_AUTHENTICATOR:
                        RECIBIDO_YA_AUTHENTICATOR = True

                registro_authenticators[serviceId] = [service,0]


    def comprueba_service_ids(self, service_id, diccionario):
        '''Verificará si el service_id argumento ya está registrado en'''
        '''un diccionario suministrado''' # pylint:disable=W0105

        id_existente = False

        for entrada in diccionario:
            if service_id == entrada:
                id_existente = True
                break

        return id_existente


    def anunciar_periodicamente(self,publicador_subscriptor,proxy_authenticator,tiempo_announce):
        '''Realizará el envío periódico del proxy y service_id del '''
        '''sirviente instancia de Authenticator''' # pylint:disable=W0105

        while True:

            print("[AUTHENTICATOR_ANNOUNCEMENTS] Va a anunciarse el authenticator\n")
            publicador_subscriptor.announce(proxy_authenticator,self.id_authenticator)
            time.sleep(tiempo_announce)


    def envejece_diccionario(self,diccionario, candado, tiempo_vigencia):
        '''Controlará el tiempo de vigencia de los service_id almacenados'''

        while True:

            with candado:
                #controlo el diccionario temporal con sección crítica

                diccionarioaux = diccionario.copy()

                for entrada in diccionarioaux:
                    if (diccionario[entrada][1]) == tiempo_vigencia:
                        print(("[AUTHENTICATOR_ANNOUNCEMENTS] Eliminado el serviceId: "
                        + f"{diccionario.pop(entrada)}\n"))
                    else:
                        diccionario[entrada][1] += 1
            time.sleep(1)





class AuthenticatorUserUpdates(IceFlix.UserUpdate):
    """Sirviente para la interfaz IceFlix.UserUpdate"""

    def __init__(self,sirviente_authenticator, referencia_authenticator):

        self.sirviente_authenticator = sirviente_authenticator
        self.referencia_authenticator = referencia_authenticator
        #dejo el token de administración nulo hasta saber si hay que pedirlo
        #a otro authenticator o usar el de mi archivo config
        self.token_administracion = None


    def set_token_administracion(self, token_administracion):
        '''Actualiza el token de administración en el Authenticator'''

        self.token_administracion = token_administracion


    def newToken(self, user, token, serviceId, current: Ice.Current=None): # pylint:disable=invalid-name, unused-argument, no-member
        '''Recibe notificaciones de creación de tokens y lo comunica al Authenticator'''

        print(f"[AUTHENTICATOR_USERUPDATES] Recibido newToken({user},{token},{serviceId})\n")
        #si el service_id es de un Authenticator conocido...
        if (self.comprueba_service_ids_authenticators( #pylint:disable=no-value-for-parameter
            serviceId,registro_authenticators,candado_registro_authenticators)):
            #hace que el Authenticator asigne el token al usuario determinado
            print(self.referencia_authenticator.isAdmin("1234"))
            self.sirviente_authenticator.impone_token_usuario(user, token)



    def revokeToken(self, token, serviceId, current: Ice.Current=None): # pylint:disable=invalid-name, unused-argument, no-member
        '''Recibe notificaciones de eliminación de tokens y lo comunica al Authenticator'''

        print(f"[AUTHENTICATOR_USERUPDATES] Recibido revokeToken({token},{serviceId})\n")
        #si el service_id es de un Authenticator conocido...
        if (self.comprueba_service_ids_authenticators( #pylint:disable=no-value-for-parameter
            serviceId,registro_authenticators,candado_registro_authenticators)):
            #hace que el Authenticator borre el token al usuario determinado
            self.sirviente_authenticator.elimina_entrada_token(token)


    def newUser(self, user, passwordHash, serviceId, current: Ice.Current=None): # pylint:disable=invalid-name, unused-argument, no-member
        '''Recibe notificaciones de creación de usuarios y lo comunica al Authenticator'''

        print(f"[AUTHENTICATOR_USERUPDATES] Recibido newUser({user},{passwordHash},{serviceId})\n")
        #si el service_id es de un Authenticator conocido...
        if (self.comprueba_service_ids_authenticators( #pylint:disable=no-value-for-parameter
            serviceId,registro_authenticators,candado_registro_authenticators)):
            #hace que el Authenticator asigne el hash al usuario determinado
            self.referencia_authenticator.addUser(user, passwordHash, self.token_administracion)


    def removeUser(self, user, serviceId, current: Ice.Current=None): # pylint:disable=invalid-name, unused-argument, no-member
        '''Recibe notificaciones de eliminación de usuarios y lo comunica al Authenticator'''

        print(f"[AUTHENTICATOR_USERUPDATES] Recibido removeUser({user},{serviceId})\n")
        #si el service_id es de un Authenticator conocido...
        if (self.comprueba_service_ids_authenticators( #pylint:disable=no-value-for-parameter
            serviceId,registro_authenticators,candado_registro_authenticators)):
            #hace que el Authenticator borre el usuario determinado
            self.referencia_authenticator.removeUser(user, self.token_administracion)


    def comprueba_service_ids_authenticators(self, service_id, diccionario, candado):
        '''Verifica que un service_id argumento sea de un Authenticator registrado'''

        id_existente = False

        with candado:
            for entrada in diccionario:
                if service_id == entrada:
                    id_existente = True
                    break

        return id_existente





class AuthenticatorData(IceFlix.AuthenticatorData):
    """Clase python para la clase IceFlix.AuthenticatorData"""

    def __init__(self):

        self.adminToken = None # pylint:disable=invalid-name
        #diccionario --> users: passwords
        self.currentUsers = None # pylint:disable=invalid-name
        #diccionario --> users: tokens
        self.activeTokens = None # pylint:disable=invalid-name


    def set_admin_token(self, admin_token):
        '''Actualiza el token de administrador'''
        self.adminToken = admin_token


    def set_current_users(self, current_users):
        '''Actualiza el diccionario de usuarios registrados'''
        self.currentUsers = current_users


    def set_active_tokens(self, active_tokens):
        '''Actualiza el diccionario de tokens activos'''
        self.activeTokens = active_tokens





class Authenticator(IceFlix.Authenticator): # pylint:disable=R0902,R0904
    """Sirviente para la interfaz IceFlix.Authenticator"""

    def __init__(self, tiempo_validez_tokens, nombre_archivo):

        self.contador_tokens_creados = 0
        # los 2 minutos durante los cuales los token mantienen su validez
        self.tiempo_validez_tokens= tiempo_validez_tokens
        self.diccionario_tokens = {}
        #se guardará el token y el tiempo de vigencia para cada usuario
        self.nombre_archivo = nombre_archivo
        #operación necesaria para inicializar el fichero
        #en caso de no existir previamente
        base_datos = open(self.nombre_archivo,"a", encoding="utf-8") # pylint:disable=R1732
        base_datos.close()
        #dejo el token de administración nulo hasta saber si hay que pedirlo
        #a otro authenticator o usar el de mi archivo config
        self.token_administracion = None
        #necesitaré una serie de candados para el archivo de usuarios
        #y el diccionario de tokens volátil
        self.candado_archivo_texto = threading.Lock()
        self.candado_lista_tokens = threading.Lock()
        #id que se verteŕa al canal UserUpdates
        self.service_id = None
        #publicador para el canal UserUpdates
        self.publicador_userupdates = None


    def set_publicador(self, publicador_userupdates):
        '''Actualiza el publicador del canal UserUpdates'''

        self.publicador_userupdates = publicador_userupdates


    def set_service_id(self, service_id):
        '''Actualiza el id del Authenticator que pblicará'''

        self.service_id = service_id


    def set_token_administracion(self, token_administracion):
        '''Actualiza el token de administración en el Authenticator'''

        self.token_administracion = token_administracion


    def set_diccionario_tokens(self, diccionario_tokens):
        '''Actualiza el diccionario de tokens temporales'''

        with self.candado_lista_tokens:
            #controlo la lista temporal de tokens con sección crítica

            self.diccionario_tokens = {}
            for entrada in diccionario_tokens:
                self.diccionario_tokens[entrada] = [diccionario_tokens[entrada],0]


    def set_nuevos_usuarios(self, diccionario_users):
        '''Actualiza el archivo con las credenciales de usuarios'''

        with self.candado_archivo_texto:
            #controlo el archivo de usuarios con sección crítica

            open(self.nombre_archivo,"w", encoding="utf-8") # pylint:disable=R1732
            for entrada in diccionario_users:
                self.inserta_credenciales_archivo(entrada,diccionario_users[entrada])


    def envejece_lista(self):
        """Controla la validez de los token con el paso del tiempo"""

        while True:

            with self.candado_lista_tokens:
                #controlo la lista temporal con sección crítica

                diccionario_aux = self.diccionario_tokens.copy()

                for entrada in diccionario_aux:
                    if (self.diccionario_tokens[entrada][1]) == self.tiempo_validez_tokens:
                        (self.publicador_userupdates.revokeToken( # pylint:disable=no-value-for-parameter
                            self.diccionario_tokens[entrada][0],self.service_id))
                        print(("[AUTHENTICATOR] Eliminada la entrada: "
                        + f"{self.diccionario_tokens.pop(entrada)}\n"))
                    else:
                        self.diccionario_tokens[entrada][1] += 1

            time.sleep(1)


    def impone_token_usuario(self, user, token):
        '''Asocia a un usuario un token temporalmente'''

        with self.candado_lista_tokens:
            print(f"[AUTHENTICATOR] Añadida/Actualizada la entrada: {[token,0]}\n")
            #inicializo su tiempo de validez
            self.diccionario_tokens[user] = [token,0]


    def elimina_entrada_token(self, token):
        '''Borra el token temporal de un usuario'''

        with self.candado_lista_tokens:

            diccionario_aux = self.diccionario_tokens.copy()
            #hay que buscarlo en la lista de tokens volátil
            for entrada in diccionario_aux:
                if self.diccionario_tokens[entrada][0] == token:
                    print(("[AUTHENTICATOR] Eliminada la entrada: "
                    + f"{self.diccionario_tokens.pop(entrada)}\n"))


    def asocia_usuario_token(self, user):
        """Inserta en la lista de token a un usuario junto con un """
        """token nuevo que no se repetirá""" # pylint:disable=W0105

        with self.candado_lista_tokens:
            #controlo la lista temporal con sección crítica

            token_usuario = "token" + str(self.contador_tokens_creados)
            # esta numeración no podrá repetirse
            #durante una ejecución (y cuando acabe se borrarán todos los datos)
            self.contador_tokens_creados += 1

            #se controla el caso de renovar el token de un usuario borrado de la lista temporal por
            # tiempo expirado (pero siga en la BD)
            # también se controla el caso de que el sistema esté recién iniciado y la lista temporal
            # vacía
            print(f"[AUTHENTICATOR] Añadida la entrada: {[token_usuario,0]}\n")
            self.diccionario_tokens[user] = [token_usuario,0]

        self.publicador_userupdates.newToken(user, token_usuario, self.service_id)

        return token_usuario


    def comprueba_credenciales(self, user, password):
        """Verifica que un usuario y contraseña estén en el """
        """arhivo de texto usado como base de datos""" # pylint:disable=W0105
        credenciales_validas = False

        with self.candado_archivo_texto:
            #controlo el archivo persistente con sección crítica

            with  open(self.nombre_archivo,"r",encoding="utf-8") as archivo_leer:
                lineas_leidas = archivo_leer.readlines()
                archivo_leer.close()

            for num_linea in range(len(lineas_leidas)): # pylint:disable=C0200
                if user == lineas_leidas[num_linea][len("[USUARIO] "):-1]:
                    if password == lineas_leidas[num_linea+1][len("[CONTRASEÑA] "):-1]:
                    #primera condición evita que falle porque la última contraseña sea igual al
                    # nombre del usuario buscado
                    #tercera condición permite comprobar si un usuario ya está registrado
                    # en la base de datos
                        credenciales_validas = True

        return credenciales_validas


    def busca_user_archivo(self, user):
        """Devuelve la línea en la que está escrito, dentro del archivo"""
        """ de texto que se usa como base de datos, el nombre de un usuario buscado""" # pylint:disable=W0105

        with self.candado_archivo_texto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombre_archivo,"r", encoding="utf-8") as archivo_leer:
                lineas_leidas = archivo_leer.readlines()
                archivo_leer.close()

            for num_linea in range(len(lineas_leidas)): # pylint:disable=C0200
                if user == lineas_leidas[num_linea][len("[USUARIO] "):-1]:
                    #[:-1] para quitar el salto de línea
                    return num_linea

        #elimina los errores que pudieran producirse si se intenta eliminar
        # un user que no existe
        return -1


    def inserta_credenciales_archivo(self, user, password):
        '''Añade a la base de datos el usuario y contraseña pasados como parámetros'''

        with open(self.nombre_archivo,"a", encoding="utf-8") as archivo_escribir:
            archivo_escribir.write("\n")
            archivo_escribir.write("[USUARIO] "+ user+"\n")
            archivo_escribir.write("[CONTRASEÑA] " + password+"\n")
            archivo_escribir.close()
        print(f"[AUTHENTICATOR] Añadidas las credenciales de: {user}\n")


    def elimina_lineas_archivo(self, num_linea):
        """Reescribe el contenido del archivo de texto usado como"""
        """base de datos saltándose ciertsa líneas""" # pylint:disable=W0105

        with self.candado_archivo_texto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombre_archivo,"r", encoding="utf-8") as archivo_leer:
                lineas_leidas = archivo_leer.readlines()
                archivo_leer.close()

            with open(self.nombre_archivo,"w", encoding="utf-8") as archivo_leer:

                for i in range(len(lineas_leidas)): # pylint:disable=C0200
                    if i not in [num_linea,num_linea + 1]: #se salta las líneas que contienen
                    #las credenciales a borrar
                        archivo_leer.write(lineas_leidas[i])
                        #ahora no añado el salto de línea porque
                        #dejaría una línea en blanco entre datos
                archivo_leer.close()


    def crea_diccionario_active_tokens(self):
        '''Genera un diccionario relacionando los usuarios y su token temporal'''

        diccionario_envio = {}

        with self.candado_lista_tokens:
            #controlo la lista temporal con sección crítica

            for entrada in self.diccionario_tokens: # pylint:disable=C0206
                diccionario_envio[entrada] = self.diccionario_tokens[entrada][0]

        return diccionario_envio


    def crea_diccionario_current_users(self):
        '''Genera un diccionario relacionando los usuarios y su contraseña'''

        diccionario_envio = {}
        lineas_leidas = []
        user = ""
        password = ""

        with self.candado_archivo_texto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombre_archivo,"r", encoding="utf-8") as archivo_leer:
                lineas_leidas = archivo_leer.readlines()
                archivo_leer.close()

        for num_linea in range(len(lineas_leidas)): # pylint:disable=C0200

            if (len("[USUARIO] ") < len(lineas_leidas[num_linea])
            and lineas_leidas[num_linea][:len("[USUARIO] ")] == "[USUARIO] "):
                #si no es una línea en blanco y en esa línea aparece un nombre de usuario...
                user = lineas_leidas[num_linea][len("[USUARIO] "):-1]
                password = lineas_leidas[num_linea+1][len("[CONTRASEÑA] "):-1]

                diccionario_envio[user] = password

        return diccionario_envio


    def refreshAuthorization(self, user, passwordHash, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Crea un nuevo token de autorización de usuario si las credenciales son válidas"

        if self.comprueba_credenciales(user, passwordHash): # pylint:disable=R1705
        #pongo True para que tenga en cuenta
        #usuario y contraseña en la comprobación
            print("[AUTHENTICATOR] Solicitado un refresco del token de: " + user+ "\n")
            token_nuevo = self.asocia_usuario_token(user)
            return token_nuevo
        else:
            raise IceFlix.Unauthorized


    def isAuthorized(self, userToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Indica si un token dado es válido o no"

        token_valido = False

        with self.candado_lista_tokens:
            #controlo la lista temporal con sección crítica

            for valor in self.diccionario_tokens.values():
                if userToken == valor[0]:
                    token_valido = True
                    break

        return token_valido


    def whois(self, userToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member, R1710
        "Permite descubrir el nombre del usuario a partir de un token válido"

        if self.isAuthorized(userToken):

            with self.candado_lista_tokens:
            #controlo la lista temporal con sección crítica

                for entrada in self.diccionario_tokens: # pylint:disable=C0206
                    if userToken == self.diccionario_tokens[entrada][0]:
                        return entrada

        else:
            raise IceFlix.Unauthorized


    def isAdmin(self, adminToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Devuelve un valor booleano para comprobar si el token proporcionado"
        "corresponde o no con el administrativo" # pylint:disable=W0105

        if adminToken == self.token_administracion: # pylint:disable=R1705, R1703
            return True
        else:
            return False


    def addUser(self, user, passwordHash, adminToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Función administrativa que permite añadir unas nuevas credenciales en el almacén de datos"
        "si el token administrativo es correcto" # pylint:disable=W0105

        if self.isAdmin(adminToken):

            if self.busca_user_archivo(user) == -1 :
            #controla el caso de querer registrar un usuario que ya existe
            #(basta con que el nombre del usuario esté en la BD)
                with self.candado_archivo_texto:
                    #controlo el archico de credenciales de usuario con sección crítica
                    self.inserta_credenciales_archivo(user,passwordHash)
                    self.publicador_userupdates.newUser(user, passwordHash, self.service_id)

                #hay que introducir al user tanto en el archivo como en la lista temporal
                #le asigno un token válido y se pone su timpo de vigencia a 0
                self.asocia_usuario_token(user)
            else:
                #si se intenta añadir un usuario que ya existía
                raise IceFlix.Unauthorized

        else:
            raise IceFlix.Unauthorized


    def removeUser(self, user, adminToken, current: Ice.Current=None):  # pylint:disable=invalid-name, unused-argument, no-member
        "Función administrativa que permite eliminar unas credenciales del almacén de"
        "datos si el token administrativo es correcto." # pylint:disable=W0105

        if self.isAdmin(adminToken):

            posicion_user_archivo = self.busca_user_archivo(user)

            if  posicion_user_archivo != -1: #controla el caso de que se intente
            #borrar un user inexistente

                #hay que borrar al user tanto del archivo ...
                self.elimina_lineas_archivo(posicion_user_archivo)

                print(f"Eliminadas las credenciales de: {user}\n")
                #... como de la lista temporal

                with self.candado_lista_tokens:
                #controlo la lista temporal con sección crítica

                    if user in self.diccionario_tokens:

                        self.publicador_userupdates.removeUser(user, self.service_id)
                        print("[AUTHENTICATOR] Eliminada la entrada: "
                        + f"{self.diccionario_tokens.pop(user)}\n")

        else:
            raise IceFlix.Unauthorized


    def bulkUpdate(self, current: Ice.Current=None): # pylint:disable=invalid-name, unused-argument, no-member
        '''Devuelve un objeto de clase AuthenticatorData con los datos de mi Authenticator'''

        authenticator_data = AuthenticatorData()
        authenticator_data.set_admin_token(self.token_administracion)
        authenticator_data.set_current_users(self.crea_diccionario_current_users())
        authenticator_data.set_active_tokens(self.crea_diccionario_active_tokens())

        return authenticator_data





class AuthenticatorApp(Ice.Application): # pylint:disable=R0902
    """Ice.Application para el servicio Authenticator."""

    def __init__(self):
        super().__init__()
        self.proxy = None
        self.service_id = None
        self.servant_authenticator = None
        self.sirviente_anunciador = None
        self.sirviente_userupdate = None
        self.hilo_envejece_tokens = None
        self.hilo_envejece_ids_authenticator = None
        self.hilo_envejece_ids_main = None
        self.hilo_announcement = None


    def run(self, args): # pylint:disable=R0914, too-many-statements
        """Ejecuta la aplicación, añadiendo los objetos necesarios al adaptador"""

        logging.info("[AUTHENTICATOR_APP] Running Authenticator application")

        ############################################################################
        #OBTENCIÓN DE LOS DATOS DEL ARCHIVO DE CONFIGURACIÓN
        ############################################################################
        properties = self.communicator().getProperties()
        token_administracion = properties.getProperty("AdminToken")
        tiempo_validez_tokens = int(properties.getProperty("TimeTokens"))
        tiempo_validez_announce = int(properties.getProperty("TimeAnnounce"))
        tiempo_validez_ids = int(properties.getProperty("TimeServiceIds"))
        tiempo_arranque = int(properties.getProperty("TimeStart"))
        nombre_archivo = properties.getProperty("BDname")
        ############################################################################

        ############################################################################
        #INSTANCIACIÓN DE LA CLASE AUTHENTICATOR Y OBTENCIÓN DE SUS DATOS
        ############################################################################
        self.servant_authenticator = Authenticator(tiempo_validez_tokens, nombre_archivo)

        adapter = (self.communicator()
        .createObjectAdapterWithEndpoints
        ("AuthenticatorAdapter",properties.getProperty("AuthenticatorAdapter.Endpoints")))
        adapter.activate()

        self.proxy = adapter.addWithUUID(self.servant_authenticator)
        print(f'\n\n[AUTHENTICATOR_APP] The proxy of the authenticator is "{self.proxy}"\n\n')
        authenticator = IceFlix.AuthenticatorPrx.uncheckedCast(self.proxy)
        #esto ya es la referencia al authenticator

        self.service_id = str(uuid.uuid4())
        print(f'[AUTHENTICATOR_APP] The service_id of the authenticator is "{self.service_id}"\n\n')
        ############################################################################

        ############################################################################
        #CREACIÓN DE CANALES , PUBLICADORES Y SUBSCRIPTORES
        ############################################################################
        topic_manager_str_prx = "IceStorm/TopicManager -t:tcp -h localhost -p 10000"
        topic_manager = IceStorm.TopicManagerPrx.checkedCast( # pylint:disable=E1101
        self.communicator().stringToProxy(topic_manager_str_prx),)

        if not topic_manager:
            raise RuntimeError("[AUTHENTICATOR_APP] Invalid TopicManager proxy")

        #Canal Announcements
        topic_name = "Announcements"
        try:
            topic = topic_manager.create(topic_name)
        except IceStorm.TopicExists: # pylint:disable=E1101
            topic = topic_manager.retrieve(topic_name)


        self.sirviente_anunciador = AuthenticatorAnnouncements(self.service_id)
        proxy_anunciador = adapter.addWithUUID(self.sirviente_anunciador)

        qos = {}

        subscriptor_publicador_announcements = topic.subscribeAndGetPublisher(qos, proxy_anunciador)
        subscriptor_publicador_announcements = topic.getPublisher()
        subscriptor_publicador_announcements = IceFlix.AnnouncementPrx.uncheckedCast(
            (subscriptor_publicador_announcements))


        #Canal UserUpdates

        topic_name = "UserUpdates"
        try:
            topic = topic_manager.create(topic_name)
        except IceStorm.TopicExists: # pylint:disable=E1101
            topic = topic_manager.retrieve(topic_name)

        self.sirviente_userupdate = AuthenticatorUserUpdates(
            self.servant_authenticator,authenticator)
        proxy_userupdate = adapter.addWithUUID(self.sirviente_userupdate)

        qos = {}

        subscriptor_publicador_userupdates = topic.subscribeAndGetPublisher(qos, proxy_userupdate)
        subscriptor_publicador_userupdates = topic.getPublisher()
        subscriptor_publicador_userupdates = IceFlix.UserUpdatePrx.uncheckedCast(
            (subscriptor_publicador_userupdates))

        self.servant_authenticator.set_publicador(subscriptor_publicador_userupdates)
        self.servant_authenticator.set_service_id(self.service_id)
        ############################################################################

        ############################################################################
        #ALGORITMO DE ARRANQUE
        ############################################################################
        print("[AUTHENTICATOR_APP] Arrancando el sistema ...")
        #esperamos a recibir anunciamientos de una instancia Main y/o Authenticator
        contador_segundos = 0
        while (not (RECIBIDO_YA_MAIN and RECIBIDO_YA_AUTHENTICATOR)
        and contador_segundos < tiempo_arranque):
            time.sleep(1) #realizo la comprobación cada segundo
            #incremento el contador para asegurar que el
            #bucle dura lo necesario
            contador_segundos += 1

        with candado_registro_mains:
            if not RECIBIDO_YA_MAIN: # si no hay ningún Main registrado se corta el programa
                raise RuntimeError("[AUTHENTICATOR_APP] No se ha recibido el anunciamiento "
                + "de ninguna instancia Main , abortando arranque ...")

        if RECIBIDO_YA_AUTHENTICATOR:
            # si hay ningún Authenticator registrado se piden sus datos
            proxy_authenticator_bd = ""
            with candado_registro_authenticators:
                for entrada in registro_authenticators: #pylint:disable=C0206
                    proxy_authenticator_bd = registro_authenticators[entrada][0]
                    break
            authenticator_bd = IceFlix.AuthenticatorPrx.uncheckedCast(proxy_authenticator_bd)
            authenticator_data = authenticator_bd.bulkUpdate()

            print("[AUTHENTICATOR_APP] Datos obtenidos para la sincronización: ")
            print("###############################################################################")
            print("     adminToken: " + authenticator_data.adminToken)
            print("     currentUsers: " + str(authenticator_data.currentUsers))
            print("     activeTokens: " + str(authenticator_data.activeTokens))
            print("###############################################################################")

            #el adminTOken debe ectualizarse en el Authenticator y el AuthenticatorUserUpdates
            self.sirviente_userupdate.set_token_administracion(authenticator_data.adminToken)
            self.servant_authenticator.set_token_administracion(authenticator_data.adminToken)
            self.servant_authenticator.set_nuevos_usuarios(authenticator_data.currentUsers)
            self.servant_authenticator.set_diccionario_tokens(authenticator_data.activeTokens)

        else: #si mi base de datos es la válida ...
            #inicializo el adminToken al valor que hay en mi archivo config
            self.servant_authenticator.set_token_administracion(token_administracion)
            self.sirviente_userupdate.set_token_administracion(token_administracion)
        ############################################################################

        ############################################################################
        #LANZAMIENTO DE HILOS NECESARIOS PARA EL CONTROL DE LA VIGENCIA DE LOS DATOS
        ############################################################################
        #hilo para anunciar el authenticator a otros servicios cada cierto tiempo
        self.hilo_announcement = threading.Thread(
            target = self.sirviente_anunciador.anunciar_periodicamente, args=(
                subscriptor_publicador_announcements,self.proxy,tiempo_validez_announce,))
        self.hilo_announcement.start()

        #hilo para eliminar referencias a otros Authenticator pasado cierto tiempo
        self.hilo_envejece_ids_authenticator = threading.Thread(
            target = self.sirviente_anunciador.envejece_diccionario, args=(
                registro_authenticators, candado_registro_authenticators, tiempo_validez_ids,))
        self.hilo_envejece_ids_authenticator.start()

        #hilo para eliminar referencias a otros Main pasado cierto tiempo
        self.hilo_envejece_ids_main = threading.Thread(
            target = self.sirviente_anunciador.envejece_diccionario, args=(
                registro_mains, candado_registro_mains, tiempo_validez_ids,))
        self.hilo_envejece_ids_main.start()

        #hilo para eliminar tokens que han estado activos más del tiempo establecido en el enunciado
        self.hilo_envejece_tokens = threading.Thread(
            target = self.servant_authenticator.envejece_lista)
        self.hilo_envejece_tokens.start()
        ############################################################################

        ############################################################################
        #CÓDIGO ANTE LA FINALIZACIÓN DEL PROGRAMA
        ############################################################################
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        topic.unsubscribe(proxy_anunciador)
        topic.unsubscribe(proxy_userupdate)
        ############################################################################

        return 0
        
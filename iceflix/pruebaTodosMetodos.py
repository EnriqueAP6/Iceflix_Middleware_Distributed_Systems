#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
import threading
import  sys
import Ice

try:
    import IceFlix

except ImportError:
    import os
    import Ice

    Ice.loadSlice(os.path.join(os.path.dirname(__file__), "iceflix.ice"))

def envejeceLista():
    
    while True: 

        contador = 0

        for elemento in listaTokens:

            if (elemento[2] + 1) == tiempoLimite:
                print(f"Se ha eliminado la entrada: {listaTokens.pop(contador)}")
            else:
                elemento[2] += 1

            contador += 1
        
        sleep(1)

        
def compruebaCredenciales(user, password, enCuentaPassword):

    credencialesValidas = False

    archivoLeer = open(nombreArchivo,"r")
    lineasLeidas = archivoLeer.readlines()

    for numLinea in range(len(lineasLeidas)):
        if user == lineasLeidas[numLinea][:-1]:
            if (numLinea +1)<= len(lineasLeidas) and password == lineasLeidas[numLinea+1][:-1] or not enCuentaPassword: 
                #primera condición evita que falle porque la última contraseña sea igual al nombre del usuario buscado
                #tercera condición permite comprobar si un usuario ya está registrado en la base de datos
                credencialesValidas = True
    
    return credencialesValidas


def asociaUsuarioToken(user):

    global contadorTokensCreados

    tokenUsuario = "token" + str(contadorTokensCreados) # esta numeración no podrá repetirse durante una ejecución (y cuando acabe se borrarán todos los datos)
    contadorTokensCreados += 1
    contadorPosicion = 0

    for elemento in listaTokens:
        if elemento[0] == user:
            listaTokens.pop(contadorPosicion)
            listaTokens.insert(contadorPosicion,[str(user),str(tokenUsuario),0])
            break
        contadorPosicion += 1

    if contadorPosicion == len(listaTokens): 
        #se controla el caso de renovar el token de un usuario borrado de la lista temporal por tiempo expirado (pero siga en la BD)
        # también se controla el caso de que el sistema esté recién iniciado y la lista temporal vacía
        listaTokens.append([user,tokenUsuario,0])

    return tokenUsuario


def buscaUserArchivo(user):

    archivoLeer = open(nombreArchivo,"r")
    lineasLeidas = archivoLeer.readlines()

    for numLinea in range(len(lineasLeidas)):
        if user == lineasLeidas[numLinea][:-1]:  #[:-1] para quitar el salto de línea
            return numLinea
    return -1 #elimina los errores que pudieran producirse si se intenta eliminar un user que no existe


def eliminaLineasArchivo(numLinea):

    archivoLeer = open(nombreArchivo,"r")
    lineasLeidas = archivoLeer.readlines()
    archivoLeer.close()
    archivoLeer = open(nombreArchivo,"w")

    for i in range(len(lineasLeidas)):
        if i != numLinea and i != numLinea + 1: #se salta las líneas que contienen las credenciales a borrar
            archivoLeer.write(lineasLeidas[i]) #ahora no añado el salto de línea porque dejaría una línea en blanco entre datos
    archivoLeer.close()


def buscaUserListaTemporal(user):

    contadorPosicion = 0

    for elemento in listaTokens:
        if elemento[0] == user:
            return contadorPosicion
        contadorPosicion += 1    


def refreshAuthorization(user, passwordHash):

    if compruebaCredenciales(user, passwordHash, True): #pongo True para que tenga en cuenta  usuario y contraseña en la comprobación
        tokenNuevo = asociaUsuarioToken(user)
        return tokenNuevo
    else:
        raise IceFlix.Unauthorized


def isAuthorized(userToken):

    tokenValido = False

    for elemento in listaTokens:
        if userToken == elemento[1]:
            tokenValido = True
    return tokenValido


def whois(userToken):

    if isAuthorized(userToken):
        for elemento in listaTokens:
            if elemento[1] == userToken:
                return elemento[0]
    else:
        raise IceFlix.Unauthorized


def isAdmin(adminToken):
    if adminToken == tokenAdministracion:
        return True
    else:
        return False


def addUser(user, passwordHash, adminToken):

    if isAdmin(adminToken):
        try:
           
            if not compruebaCredenciales(user, passwordHash, False): #controla el caso de querer registrar un usuario que ya existe
                archivoEscribir = open(nombreArchivo,"a")
                archivoEscribir.write(user+"\n")
                archivoEscribir.write(passwordHash+"\n")
                archivoEscribir.close()

                #hay que introducir al user tanto en el archivo como en la lista temporal
                listaTokens.append([user,'',0]) #introduzco en la lista temporal al nuevo usuario, pero con valores vacios 
                asociaUsuarioToken(user) #le asigno un token válido al user y se pone su edad a 0

        except:
            raise IceFlix.TemporaryUnavailable
    else:
        raise IceFlix.Unauthorized


def removeUser(user, adminToken):

    if isAdmin(adminToken):
        try:
            posicionUserArchivo = buscaUserArchivo(user)

            if  posicionUserArchivo != -1: #controla el caso de que se intente borrar un user inexistente
                eliminaLineasArchivo(posicionUserArchivo)  #hay que borrar al user tanto del archivo ...
                listaTokens.pop(buscaUserListaTemporal(user)) #... como de la lista temporal
        except:
            raise IceFlix.Unauthorized
    else:
        raise IceFlix.Unauthorized 


def imprimeListaTokens():
    
    for elemento in listaTokens:
        print(elemento)



if __name__ == "__main__":

    tokenAdministracion = "1234"
    contadorTokensCreados = 0
    tiempoLimite= 15
    listaTokens = []
    nombreArchivo = "bbddCredenciales.txt"

    

    #ESTO LUEGO LO HARÍA EL adduser()
    listaTokens.append(['EnriqueAP6','token1',10])
    listaTokens.append(['user2','token2',3])
    listaTokens.append(['eap_6','token3',6])
    listaTokens.append(['user4','token4',8])
    listaTokens.append(['efjvdj','token5',5])
    listaTokens.append(['user6','token6',2])
    listaTokens.append(['user','token7',0])
    ######################################

    imprimeListaTokens()
    print(isAuthorized("token4"))
    print(isAuthorized("token42"))


    #hilo = threading.Thread(target = envejeceLista)
    #hilo.start()

    #sleep(3)

    #while True:
    #    listaTokens.append(['user8','token8',11])
    #    print(isAuthorized("token2"))
    #    print(isAuthorized("token6"))
    #    sleep(5)



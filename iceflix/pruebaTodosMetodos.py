#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
import threading


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


def introducirDatoArchivo(lineaEscribir):
    
    archivoEscribir = open(nombreArchivo,"a")
    archivoEscribir.write(lineaEscribir+"\n")
    archivoEscribir.close()
        
def compruebaCredenciales(nombreArchivo, user, password):

    credencialesValidas = False

    archivoLeer = open(nombreArchivo,"r")
    lineasLeidas = archivoLeer.readlines()

    for numLinea in range(len(lineasLeidas)):
        if user == lineasLeidas[numLinea][:-1]:
            if (numLinea +1)<= len(lineasLeidas) and password == lineasLeidas[numLinea+1][:-1]: #primera condición evita que falle porque la última contraseña sea igual a un usuario
                credencialesValidas = True
    
    return credencialesValidas


def asociaUsuarioToken(user):

    global contadorTokensCreados

    tokenUsuario = "token" + str(contadorTokensCreados)
    contadorTokensCreados += 1
    contadorPosicion = 0

    for elemento in listaTokens:
        if elemento[0] == user:
            listaTokens.pop(contadorPosicion)
            listaTokens.insert(contadorPosicion,[str(user),str(tokenUsuario),0])
            break
        contadorPosicion += 1

    return tokenUsuario


def refreshAuthorization(user, passwordHash):

    if compruebaCredenciales(nombreArchivo, user, passwordHash):
        tokenNuevo = asociaUsuarioToken(user)
        return tokenNuevo
    #else:
        #raise IceFlix.Unauthorized


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
    #else:
        #raise IceFlix.Unauthorized



def isAdmin(adminToken):
    if adminToken == tokenAdministracion:
        return True
    else:
        return False


def imprimeListaTokens():
    
    for elemento in listaTokens:
        print(elemento)






if __name__ == "__main__":

    tokenAdministracion = "1234"
    contadorTokensCreados = 0
    tiempoLimite= 15
    listaTokens = []
    nombreArchivo = "bbddCredenciales.txt"

    #introducirDatoArchivo("EnriqueAP6")
    #introducirDatoArchivo("010203")
    #introducirDatoArchivo("eap_6")
    #introducirDatoArchivo("102030")
    #introducirDatoArchivo("efjvdj")
    #introducirDatoArchivo("odiewsnjd")
    #introducirDatoArchivo("user")
    #introducirDatoArchivo("password")

    #ESTO LUEGO LO HARÍA EL adduser()
    listaTokens.append(['EnriqueAP6','token1',10])
    listaTokens.append(['user2','token2',3])
    listaTokens.append(['eap_6','token3',6])
    listaTokens.append(['user4','token4',8])
    listaTokens.append(['efjvdj','token5',5])
    listaTokens.append(['user6','token6',2])
    listaTokens.append(['user','token7',0])
    ######################################
    
    

    #hilo = threading.Thread(target = envejeceLista)
    #hilo.start()

    #sleep(3)

    #while True:
    #    listaTokens.append(['user8','token8',11])
    #    print(isAuthorized("token2"))
    #    print(isAuthorized("token6"))
    #    sleep(5)



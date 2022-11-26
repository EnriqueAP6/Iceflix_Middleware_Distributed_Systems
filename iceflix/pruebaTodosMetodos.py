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
    
    archivoEscribir = open(nombreArchivo,"w")
    
    archivoEscribir.write(lineaEscribir[0]+"\n")
    archivoEscribir.write(lineaEscribir[1]+"\n")

    archivoEscribir.close()

        
def compruebaCredenciales(nombreArchivo, user, password):

    credencialesValidas = False

    archivoLeer = open(nombreArchivo,"r")
    lineasLeidas = archivoLeer.readlines()

    for numLinea in range(len(lineasLeidas)):

        if user == lineasLeidas[numLinea][:-1]:
            if (numLinea +1)<= len(lineasLeidas) and password == lineasLeidas[numLinea+1][:-1]:
                credencialesValidas = True
    
    return credencialesValidas


def isAuthorized(tokenUsuario):
    #después de comprobar sus credenciales

    tokenValido = False

    for elemento in listaTokens:
        if tokenUsuario == elemento[1]:
            tokenValido = True
    return tokenValido


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

    return tokenUsuario,contadorTokensCreados


def refreshAuthorization(user, passwordHash):
    
    if compruebaCredenciales(nombreArchivo, user, passwordHash):
        tokenNuevo = asociaUsuarioToken(user)
    else:
        raise IceFlix.Unauthorized


def imprimeListaTokens():
    
    for elemento in listaTokens:
        print(elemento)







if __name__ == "__main__":

    contadorTokensCreados = 0
    tiempoLimite= 15
    listaTokens = []
    nombreArchivo = "bbddCredenciales.txt"

    introducirDatoArchivo("EnriqueAP6")
    introducirDatoArchivo("010203")
    introducirDatoArchivo("eap_6")
    introducirDatoArchivo("102030")
    introducirDatoArchivo("efjvdj")
    introducirDatoArchivo("odiewsnjd")
    introducirDatoArchivo("user")
    introducirDatoArchivo("password")

    #ESTO LUEGO LO HARÍA EL adduser()
    listaTokens.append(['EnriqueAP6','token',10])
    listaTokens.append(['user2','token',3])
    listaTokens.append(['eap_6','token',6])
    listaTokens.append(['user4','token',8])
    listaTokens.append(['efjvdj','token',5])
    listaTokens.append(['user6','token',2])
    listaTokens.append(['user','token',0])
    ######################################



    tokenNuevo = asociaUsuarioToken('EnriqueAP6')
    tokenNuevo = asociaUsuarioToken('eap_6')
    tokenNuevo = asociaUsuarioToken('user')
    tokenNuevo = asociaUsuarioToken('user4')
    tokenNuevo = asociaUsuarioToken('efjvdj')
    tokenNuevo = asociaUsuarioToken('user6')
    
    imprimeListaTokens()
    tokenNuevo = asociaUsuarioToken('EnriqueAP6')
    print()
    imprimeListaTokens()

#hilo = threading.Thread(target = envejeceLista)
#hilo.start()

#print(isAuthorized("token2"))
#print(isAuthorized("token32"))
#print(isAuthorized("token7"))

#sleep(3)

#while True:
#    lista.append(['user8','token8',11])
#    sleep(5)



#print(compruebaCredenciales(nombreArchivo,"eap_6","102030"))
#print(compruebaCredenciales(nombreArchivo,"eap_6","password"))
#print(compruebaCredenciales(nombreArchivo,"user","password"))


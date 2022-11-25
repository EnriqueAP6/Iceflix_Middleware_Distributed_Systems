#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
import threading

tiempoLimite= 15
lista = []
lista.append(['user1','token1',10])
lista.append(['user2','token2',3])
lista.append(['user3','token3',6])
lista.append(['user4','token4',8])
lista.append(['user5','token5',5])
lista.append(['user6','token6',2])
lista.append(['user7','token7',0])

def envejeceLista():
    
    while True: #len(lista) != 0:

        contador = 0

        for elemento in lista:

            if (elemento[2] + 1) == tiempoLimite:
                print(f"Se ha eliminado la entrada: {lista.pop(contador)}")
            else:
                elemento[2] += 1

            contador += 1
        
        sleep(1)

def compruebaValidezToken(tokenUsuario):
    #después de comprobar sus credenciales

    tokenValido = False

    for entrada in lista:
        if tokenUsuario == entrada[1]:
            tokenValido = True
    return tokenValido



hilo = threading.Thread(target = envejeceLista)
hilo.start()

print(compruebaValidezToken("token2"))
print(compruebaValidezToken("token32"))
print(compruebaValidezToken("token7"))

sleep(3)

while True:
    lista.append(['user8','token8',11])
    sleep(5)





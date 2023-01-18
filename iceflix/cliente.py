#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /cliente.py <'PROXY DEL AUTHENTICATOR'> desde esta carpeta
import sys
import Ice
import time
Ice.loadSlice('iceflix.ice')
import IceFlix




class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        authenticator = IceFlix.AuthenticatorPrx.checkedCast(proxy)

        if not authenticator:
            raise RuntimeError('Invalid proxy')
        while 1:
            self.menu(authenticator)
        return 0
    def menu(self, authenticator):
        print("----------------------------------------------")
        print("Elegir una opcion:")
        print("1. refreshAuthorization()")
        print("2. isAuthorized()")
        print("3. whois()")
        print("4. isAdmin()")
        print("5. addUser()")
        print("6. removeUser()")
        opcion = input()
        if opcion == "1":
            print("user: ")
            user = input()
            print("pwd: ")
            pwd = input()
            try:
                print(authenticator.refreshAuthorization(user, pwd))
                #print(authenticator.refreshAuthorization("US1", "C1"))
            except:
                print("Ha habido un error")
        if opcion == "2":
            print("token de usuario: ")
            user = input()
            #try:
            print(authenticator.isAuthorized(user))
                #print(authenticator.isAuthorized("1234"))
            #except:
            #    print("Ha habido un error")
        if opcion == "3":
            print("token de usuario: ")
            user = input()
            try:
                print(authenticator.whois(user))
                #print(authenticator.whois("1234"))
            except:
                print("Ha habido un error")
        if opcion == "4":
            print("tokenadmin: ")
            token = input()
            try:
                print(authenticator.isAdmin(token))
                #print(authenticator.isAdmin("1234"))
            except:
                print("Ha habido un error")
        if opcion == "5":
            print("user: ")
            user = input()
            print("pwd: ")
            pwd = input()
            print("tokenadmin: ")
            token = input()
            try:
                authenticator.addUser(user, pwd, token)
                #authenticator.addUser("US6", "C6", "1234")
            except:
                print("Ha habido un error")
        if opcion == "6":
            print("user: ")
            user = input()
            print("tokenadmin: ")
            token = input()
            try:
                authenticator.removeUser(user, token)
                #authenticator.removeUser("US6", "1234")
            except:
                print("Ha habido un error")
        

sys.exit(Client().main(sys.argv))
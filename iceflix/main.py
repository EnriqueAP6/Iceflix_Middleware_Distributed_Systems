#!/usr/bin/python3
# -*- coding: utf-8 -*-
# python3 iceflix/main.py --Ice.Config=configs/main.config desde fuera de esta carpeta
"""Module containing a template for a main service."""

import logging
import sys
import time
import Ice
import threading
import IceStorm
import random
#from iceflix.announcementMAINPRUEBA import AnnouncementServantMAINPRUEBA
from datetime import datetime
Ice.loadSlice("iceflix/iceflix.ice")
import IceFlix  
#pylint:disable=import-error
# python3 iceflix/main2.py --Ice.Config=configs/main.config
class MainI(IceFlix.Main):
    def __init__(self, token):
        self.admin_token = token
        self.authenticator = []
        self.catalog = []
        self.ServiceID = ""
    def isAdmin(self, admin_token, current=None):
        return admin_token == self.admin_token
    def newService(self, service, service_id,current=None):
        print("NEW SERVICE")
        if service.ice_isA('::IceFlix::Authenticator'):
            print("soy authenticator "+ str(service_id))
            self.authenticator.append(service)
        elif service.ice_isA('::IceFlix::MediaCatalog'):
            print("soy catalog")
            self.catalog.append(service)
        else:
            raise IceFlix.UnknownService()
    def getAuthenticator(self, current):  # pylint:disable=invalid-name, unused-argument
        while True:
            if not self.authenticator:
                raise IceFlix.TemporaryUnavailable()
            auth = random.choice(self.authenticator)
            if not auth:
                raise IceFlix.TemporaryUnavailable()
            try:
                auth.ice_ping()
            except RuntimeError:
                self.authenticator.remove(auth)
            return IceFlix.AuthenticatorPrx.uncheckedCast(auth)

    def getCatalog(self, current):  # pylint:disable=invalid-name, unused-argument
        while True:
            if not self.catalog:
                raise IceFlix.TemporaryUnavailable()
            catalog = random.choice(self.catalog)
            if not catalog:
                raise IceFlix.TemporaryUnavailable()
            try:
                catalog.ice_ping()
            except RuntimeError:
                self.catalog.remove(catalog)
            return IceFlix.MediaCatalogPrx.uncheckedCast(catalog)

    def announce(self, proxy, service_id, current):  # pylint:disable=invalid-name, unused-argument
        "Announcements handler."
        print("Anuncio de: " + str(proxy) + ", con service_id: "+ str(service_id))
        # TODO: implement
        return


class AnnouncementServantMAINPRUEBA(IceFlix.AnnouncementMAINPRUEBA):
    def __init__(self):
        pass
    def announce(self, service, serviceId, current=None):
        if service.ice_isA('::IceFlix::Main'):
            print("RECIBIDO UN MAIN " + str(serviceId))
        elif service.ice_isA('::IceFlix::Authenticator'):
            print("RECIBIDO UN AUTHENTICATOR "+ str(serviceId))
        else:
            print("SERVICIO NO INTERESANTE")


class MainS(Ice.Application):
    def __init__(self):
        self.servant = None
        self.broker = None
        self.service_id =""
        self.Announcement = None

    def run(self, args):
        self.broker = self.communicator()
        self.service_id = "MAIN PRUEBA 123XD"
        self.servant = MainI(
            self.communicator().getProperties().getProperty('AdminToken'))
        adapter = self.broker.createObjectAdapterWithEndpoints("MainAdapter","tcp")
        proxy = adapter.add(self.servant, self.broker.stringToIdentity(self.service_id))
        print(proxy, flush=True)
        
        adapter.activate()

        subscriber_Announcement, adapter_Announcement, servant_Announcements = self.get_topic_Announcements()
        qos_Announcement = {}
        self.Announcement.subscribeAndGetPublisher(qos_Announcement, subscriber_Announcement)
        Announcement_publisher = self.Announcement.getPublisher()
        Announcement_publisher = IceFlix.AnnouncementMAINPRUEBAPrx.uncheckedCast(Announcement_publisher)
        print("Waiting events... '{}'".format(subscriber_Announcement))        
        adapter_Announcement.activate()
        self.servant.ServiceID = self.service_id
        #timestamp = int(round(datetime.now().timestamp()))
        self.hilo_annuncio2 = threading.Thread(target=self.hilo_anuncios, args=(Announcement_publisher, proxy, ))
        self.hilo_annuncio2.start()

        self.shutdownOnInterrupt()
        self.broker.waitForShutdown()
        self.Announcement.unsubscribe(subscriber_Announcement)
        return 0
    

    def get_topic_Announcements(self):
        topic_mgr = "IceStorm/TopicManager -t:tcp -h localhost -p 10000"
        topic_manager = IceStorm.TopicManagerPrx.checkedCast( # pylint:disable=E1101
        self.communicator().stringToProxy(topic_mgr),)
        if not topic_manager:
            print("Invalid proxy")
            return 2
        servant = AnnouncementServantMAINPRUEBA()
        adapter = self.broker.createObjectAdapterWithEndpoints("AnnouncementsAdapter","tcp")
        subscriber = adapter.addWithUUID(servant)

        topic_name = "Announcements"
        qos = {}
        try:
            topic = topic_manager.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_manager.create(topic_name)
        self.Announcement = topic
        servant.Announcements = topic
        return subscriber, adapter, servant
    
    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None

        print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def hilo_anuncios(self, Announcement_publisher, proxy):
        while 1:
            Announcement_publisher.announce(proxy, self.service_id)
            time.sleep(8)

server = MainS()
sys.exit(server.main(sys.argv))
    
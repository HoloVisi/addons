# -*- coding: utf-8 -*-
import holo
import xbmc
import xbmcgui
import time
import threading
import socket
import os


class service_thread(xbmc.Monitor, threading.Thread):
            
    def __init__(self, holoMain):
        try:

            holoMain.dbg_log('_service_::__init__', 'enter_function', 0)

            self.holo = holoMain
            
            self.wait_evt = threading.Event()
            
            self.socket_file = '/var/run/service.holovisi.settings.sock'

            self.sock = socket.socket(socket.AF_UNIX,
                    socket.SOCK_STREAM)
            self.sock.setblocking(1)

            if os.path.exists(self.socket_file):
                os.remove(self.socket_file)

            self.sock.bind(self.socket_file)
            self.sock.listen(1)

            self.stopped = False
            
            threading.Thread.__init__(self)

            self.daemon = True
            
            self.holo.dbg_log('_service_::__init__', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('_service_::__init__', 'ERROR: (' + repr(e) + ')')

    def stop(self):
        try:

            self.holo.dbg_log('_service_::stop', 'enter_function', 0)

            self.stopped = True

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_file)
            sock.send('exit')
            sock.close()
            self.sock.close()
            
            self.holo.dbg_log('_service_::stop', 'enter_function', 0)

        except Exception, e:
            self.holo.dbg_log('_service_::stop', 'ERROR: (' + repr(e) + ')')

    def run(self):
        try:

            self.holo.dbg_log('_service_::run', 'enter_function', 0)

            while self.stopped is False:

                (conn, addr) = self.sock.accept()
                message = conn.recv(1024)
                self.holo.dbg_log('_service_::run', 'MESSAGE:' + repr(message), 1)
                conn.close()

                if message == 'openConfigurationWindow':
                    self.holo.openConfigurationWindow()

                if message == 'exit':
                    self.stopped = True

            self.holo.dbg_log('_service_::run', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('_service_::run', 'ERROR: (' + repr(e) + ')')

    def onAbortRequested(self):
        self.wait_evt.set()

    def onScreensaverActivated(self):
        self.wait_evt.set()
        
holo.load_modules()
holo.start_service()

monitor = service_thread(holo.__holo__)

monitor.start()

while not monitor.wait_evt.wait(1) and not xbmc.abortRequested:
    pass

holo.stop_service()
monitor.stop()

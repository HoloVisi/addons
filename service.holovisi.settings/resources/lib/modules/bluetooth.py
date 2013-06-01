# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import xbmc
import xbmcgui
import time
import dbus
import dbus.service
import threading
import gobject
import holoWindows


class bluetooth:

    menu = {'5': {
        'name': 32331,
        'menuLoader': 'menu_connections',
        'listTyp': 'btlist',
        'InfoText': 704,
        }}
    bt_daemon = '/usr/lib/bluetooth/bluetoothd'

    def __init__(self, holoMain):
        try:

            holoMain.dbg_log('bluetooth::__init__', 'enter_function', 0)

            self.discovery_time = 30  # Seconds
            self.listItems = {}
            self.holo = holoMain
            self.bt_support = True
            self.dbusSystemBus = self.holo.dbusSystemBus
            self.update_menu = False
            self.active = False
            self.dbusBluezAdapter = None
            
            self.holo.dbg_log('bluetooth::__init__', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('bluetooth::__init__', 'ERROR: (' + repr(e) + ')', 4)

    def do_init(self):
        try:

            self.holo.dbg_log('bluetooth::do_init', 'enter_function', 0)
        
            if hasattr(self, 'dbusMonitor'):
                self.dbusMonitor.initialize_agent()
            
            self.active = True
            
            self.holo.dbg_log('bluetooth::do_init', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('bluetooth::do_init', 'ERROR: (' + repr(e) + ')')

    def start_service(self):
        try:

            self.holo.dbg_log('bluetooth::start_service', 'enter_function'
                            , 0)

            self.dbusMonitor = monitorLoop(self.holo)
            self.dbusMonitor.start()

            self.holo.dbg_log('bluetooth::start_service', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('bluetooth::start_service', 'ERROR: (' + repr(e) + ')')

    def stop_service(self):
        try:

            self.holo.dbg_log('bluetooth::stop_service', 'enter_function'
                            , 0)
            
            if hasattr(self, 'dbusMonitor'):
                self.dbusMonitor.exit()
                del self.dbusMonitor
                
            if hasattr(self, 'discovery_thread'):
                self.discovery_thread.stop()
                del self.discovery_thread
                
            self.stop_bluetoothd()
            if hasattr(self, 'dbusSystemBus'):
                del self.dbusSystemBus

            if hasattr(self, 'dbusBluezManager'):
                self.dbusBluezManager = None
                del self.dbusBluezManager

            if hasattr(self, 'dbusBluezAdapter'):
                self.dbusBluezAdapter = None

            self.holo.dbg_log('bluetooth::stop_service', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('bluetooth::stop_service', 'ERROR: (' + repr(e) + ')')

    def start_bluetoothd(self):
        try:

            self.holo.dbg_log('bluetooth::start_bluetoothd',
                            'enter_function', 0)
      
            pid = self.holo.execute('pidof %s'
                    % os.path.basename(self.bt_daemon)).split(' ')
            if pid[0] == '':
                  
                self.holo.dbg_log('bluetooth::init_bluetooth',
                                'Starting Bluetooth Daemon.', 0)
                os.system(self.bt_daemon + ' &')      
                
            self.holo.dbg_log('bluetooth::start_bluetoothd',
                            'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('bluetooth::start_bluetoothd', 'ERROR: (' + repr(e) + ')', 4)

    def stop_bluetoothd(self):
        try:

            self.holo.dbg_log('bluetooth::stop_bluetoothd',
                            'enter_function', 0)

            if self.dbusBluezAdapter != None:
                self.adapter_powered( \
                  self.dbusBluezAdapter, 0)
                self.dbusBluezAdapter = None
                
            if hasattr(self, 'dbusMonitor'):
                if hasattr(self.dbusMonitor, 'btAgent'):
                    self.dbusMonitor.initialize_agent(False)
              
            pid = self.holo.execute('pidof %s'
                                  % os.path.basename(self.bt_daemon)).split(' '
                    )
            for p in pid:
                os.system('kill ' + p.strip().replace('\n', ''))

            self.holo.dbg_log('bluetooth::stop_bluetoothd',
                            'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('services::stop_bluetoothd', 'ERROR: (' + repr(e) + ')', 4)

    def get_adapter(self):
        try:

            self.holo.dbg_log('bluetooth::get_adapter', 'enter_function',
                            0)

            dbusManagedObjects = \
                self.dbusBluezManager.GetManagedObjects()

            for (path, ifaces) in dbusManagedObjects.iteritems():
                dbusBluezAdapter = ifaces.get('org.bluez.Adapter1')
                if dbusBluezAdapter != None:
                    dbusBluezAdapter = \
                        dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                            , path), 'org.bluez.Adapter1')
                    break

            dbusManagedObjects = None
            del dbusManagedObjects

            if dbusBluezAdapter is None:
                self.bt_support = False
                self.holo.dbg_log('bluetooth::get_adapter',
                                'exit_function (No Adapter Found)', 0)

            self.holo.dbg_log('bluetooth::get_adapter', 'exit_function',
                            0)

            return dbusBluezAdapter
          
        except Exception, e:
            self.holo.dbg_log('bluetooth::get_adapter', 'ERROR: (' + repr(e) + ')', 4)

    def get_devices(self):
        try:

            devices = {}

            self.holo.dbg_log('bluetooth::get_devices', 'enter_function',
                            0)

            managedObjects = self.dbusBluezManager.GetManagedObjects()

            for (path, interfaces) in managedObjects.iteritems():
                if 'org.bluez.Device1' in interfaces:
                    devices[path] = interfaces['org.bluez.Device1']

            managedObjects = None
            del managedObjects

            self.holo.dbg_log('bluetooth::get_devices', 'exit_function', 0)
            return devices

        except Exception, e:

            self.holo.dbg_log('bluetooth::get_devices::__init__',
                            'ERROR: (' + repr(e) + ')', 4)

    def exit(self):
        try:

            self.holo.dbg_log('bluetooth::exit', 'enter_function', 0)

            self.active = False
            
            if hasattr(self, 'discovery_thread'):
                self.discovery_thread.stop()
                del self.discovery_thread
                
            if hasattr(self, 'dbusBluezManager'):
                self.dbusBluezManager = None
                del self.dbusBluezManager

            if hasattr(self, 'dbusBluezAdapter'):
                self.dbusBluezAdapter = None
                
            if hasattr(self, 'dbusMonitor'):
                self.dbusMonitor.initialize_agent(False)
                
            self.clear_list()

            self.holo.dbg_log('bluetooth::exit', 'exit_function', 0)
            pass
        except Exception, e:

            self.holo.dbg_log('bluetooth::exit', 'ERROR: (' + repr(e)
                            + ')')

    def clear_list(self):
        try:

            remove = [entry for entry in self.listItems]
            for entry in remove:
                del self.listItems[entry]
        except Exception, e:

            self.holo.dbg_log('bluetooth::clear_list', 'ERROR: ('
                            + repr(e) + ')', 4)

    def menu_connections(self, focusItem=None):

        try:

            if self.update_menu == True:
                return
              
            if self.holo.read_setting('system', 'disable_bt') == '1':
                self.bt_support = False
                self.holo.winHoloMain.getControl(1301).setLabel(self.holo._(32346))
                self.clear_list()
                self.holo.winHoloMain.getControl(int(self.holo.listObject['btlist'
                        ])).reset()                
                return

            self.init_adapter()
                            
            if self.dbusBluezAdapter == None:
                self.bt_support = False
                self.holo.winHoloMain.getControl(1301).setLabel(self.holo._(32338))
                self.clear_list()
                self.holo.winHoloMain.getControl(int(self.holo.listObject['btlist'
                        ])).reset()                
                return
            
            self.holo.winHoloMain.getControl(1301).setLabel(self.holo._(32339))
            self.update_menu = True
            self.bt_support = True
            
            if not hasattr(self, 'discovery_thread'):
                self.start_discovery()
                self.discovery_thread = discoveryThread(self.holo)
                self.discovery_thread.start()
            else:
                if self.discovery_thread.stopped:
                    self.discovery_thread = None
                    self.start_discovery()
                    self.discovery_thread = discoveryThread(self.holo)
                    self.discovery_thread.start()
                
            self.holo.dbg_log('bluetooth::menu_connections',
                            'enter_function', 0)

            dictProperties = {}

            # type 1=int, 2=string, 3=array, 4=bool
            properties = {
                0: {'type': 4, 'value': 'Paired'},
                1: {'type': 2, 'value': 'Adapter'},
                2: {'type': 4, 'value': 'Connected'},
                3: {'type': 2, 'value': 'Address'},
                5: {'type': 1, 'value': 'Class'},
                6: {'type': 4, 'value': 'Trusted'},
                7: {'type': 2, 'value': 'Icon'},
                }

            rebuildList = 0
            self.dbusDevices = self.get_devices()
            if len(self.dbusDevices) != len(self.listItems):
                rebuildList = 1
                self.holo.winHoloMain.getControl(int(self.holo.listObject['btlist'
                        ])).reset()
                self.clear_list()
            else:

                for dbusDevice in self.dbusDevices:
                    if dbusDevice not in self.listItems:
                        rebuildList = 1
                        self.holo.winHoloMain.getControl(int(self.holo.listObject['btlist'
                                ])).reset()
                        self.clear_list()
                        break

            for dbusDevice in self.dbusDevices:

                dictProperties = {}

                apName = ''

                dictProperties['entry'] = dbusDevice
                dictProperties['modul'] = self.__class__.__name__
                dictProperties['action'] = 'open_context_menu'

                if 'Name' in self.dbusDevices[dbusDevice]:
                    apName = self.dbusDevices[dbusDevice]['Name']

                if not 'Icon' in self.dbusDevices[dbusDevice]:
                    dictProperties['Icon'] = 'default'

                for prop in properties:

                    name = properties[prop]['value']

                    if name in self.dbusDevices[dbusDevice]:
                        value = self.dbusDevices[dbusDevice][name]

                        if name == 'Connected':
                            if value:
                                dictProperties['ConnectedState'] = \
                                    self.holo._(32333) + '[COLOR white]' \
                                    + self.holo._(32334) + '[/COLOR]'
                            else:
                                dictProperties['ConnectedState'] = \
                                    self.holo._(32333) + '[COLOR white]' \
                                    + self.holo._(32335) + '[/COLOR]'

                        if properties[prop]['type'] == 1:
                            value = str(int(value))
                        if properties[prop]['type'] == 2:
                            value = str(value)
                        if properties[prop]['type'] == 3:
                            value = str(len(value))
                        if properties[prop]['type'] == 4:
                            value = str(int(value))

                        dictProperties[name] = value

                if rebuildList == 1:
                    self.listItems[dbusDevice] = \
                        self.holo.winHoloMain.addConfigItem(apName,
                            dictProperties, self.holo.listObject['btlist'
                            ])
                else:

                    if self.listItems[dbusDevice] != None:
                        self.listItems[dbusDevice].setLabel(apName)
                        for dictProperty in dictProperties:
                            self.listItems[dbusDevice].setProperty(dictProperty,
                                    dictProperties[dictProperty])

            self.update_menu = False

            self.holo.dbg_log('bluetooth::menu_connections',
                            'exit_function', 0)
        except Exception, e:
            self.update_menu = False
            self.holo.dbg_log('bluetooth::menu_connections', 'ERROR: ('
                            + repr(e) + ')', 4)

    def open_context_menu(self, listItem):
        try:

            self.holo.dbg_log('bluetooth::show_options', 'enter_function'
                            , 0)

            values = {}

            if listItem is None:
                listItem = \
                    self.holo.winHoloMain.getControl(self.holo.listObject['btlist'
                        ]).getSelectedItem()

            if listItem.getProperty('Connected') == '1':
                values[1] = {'text': self.holo._(32143),
                             'action': 'disconnect_device'}
            else:
                values[1] = {'text': self.holo._(32144),
                             'action': 'init_device'}
                values[2] = {'text': self.holo._(32358),
                             'action': 'trust_connect_device'}

            values[3] = {'text': self.holo._(32141),
                         'action': 'remove_device'}
            values[4] = {'text': self.holo._(32142),
                         'action': 'menu_connections'}

            context_menu = holoWindows.contextWindow('contexMenu.xml',
                    self.holo.__cwd__, 'Default', holoMain=self.holo)  #
            context_menu.options = values
            context_menu.doModal()

            if context_menu.result != '':
                getattr(self, context_menu.result)(listItem)

            del context_menu

            self.holo.dbg_log('bluetooth::show_options', 'exit_function',
                            0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::show_options', 'ERROR: ('
                            + repr(e) + ')', 4)

    def create_context_entry(
        self,
        order,
        label,
        action,
        ):

        value = {}
        value[order] = {}
        value[order]['label'] = label
        value[order]['action'] = action

    def init_device(self, listItem=None):
        try:

            self.holo.dbg_log('bluetooth::init_device', 'exit_function',
                            0)

            if listItem is None:
                listItem = \
                    self.holo.winHoloMain.getControl(self.holo.listObject['btlist'
                        ]).getSelectedItem()

            if listItem is None:
                return

            #if self.discovering == True:
            #    self.stop_discovery()

            if listItem.getProperty('Paired') != '1':
                self.pair_device(listItem.getProperty('entry'))
            else:

                self.connect_device(listItem.getProperty('entry'))

            self.holo.dbg_log('bluetooth::init_device', 'exit_function',
                            0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::init_device', 'ERROR: ('
                            + repr(e) + ')', 4)

    def trust_connect_device(self, listItem=None):
        try:

            self.holo.dbg_log('bluetooth::trust_connect_device',
                            'exit_function', 0)

            if listItem is None:
                listItem = \
                    self.holo.winHoloMain.getControl(self.holo.listObject['btlist'
                        ]).getSelectedItem()

            if listItem is None:
                return

            #if self.discovering == True:
            #    self.stop_discovery()

            self.trust_device(listItem.getProperty('entry'))
            self.connect_device(listItem.getProperty('entry'))

            self.holo.dbg_log('bluetooth::trust_connect_device',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::trust_connect_device',
                            'ERROR: (' + repr(e) + ')', 4)

    def pair_device(self, path):
        try:

            self.holo.set_busy(1)

            self.holo.dbg_log('bluetooth::pair_device', 'enter_function',
                            0)

            device = \
                dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                               , path), 'org.bluez.Device1')
            device.Pair(reply_handler=self.pair_reply_handler,
                        error_handler=self.dbus_error_handler)

            self.holo.dbg_log('bluetooth::pair_device', 'exit_function',
                            0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::pair_device', 'ERROR: ('
                            + repr(e) + ')', 4)

    def pair_reply_handler(self):
        try:

            self.holo.dbg_log('bluetooth::pair_reply_handler',
                            'enter_function', 0)

            self.holo.set_busy(0)

            listItem = \
                self.holo.winHoloMain.getControl(self.holo.listObject['btlist'
                    ]).getSelectedItem()

            if listItem is None:
                return

            self.trust_device(listItem.getProperty('entry'))
            self.connect_device(listItem.getProperty('entry'))
            self.menu_connections()

            self.holo.dbg_log('bluetooth::pair_reply_handler',
                            'exit_function', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::pair_reply_handler', 'ERROR: ('
                            + repr(e) + ')', 4)

    def trust_device(self, path):
        try:

            self.holo.set_busy(1)

            self.holo.dbg_log('bluetooth::trust_device', 'enter_function'
                            , 0)

            prop = \
                dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                               , path),
                               'org.freedesktop.DBus.Properties')

            prop.Set('org.bluez.Device1', 'Trusted', True)

            self.holo.dbg_log('bluetooth::trust_device', 'exit_function',
                            0)

            self.holo.set_busy(0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::trust_device', 'ERROR: ('
                            + repr(e) + ')', 4)

    def connect_device(self, path):
        try:

            self.holo.set_busy(1)

            self.holo.dbg_log('bluetooth::connect_device',
                            'enter_function', 0)

            device = \
                dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                               , path), 'org.bluez.Device1')
            device.Connect(reply_handler=self.connect_reply_handler,
                           error_handler=self.dbus_error_handler)

            self.holo.dbg_log('bluetooth::connect_device', 'exit_function'
                            , 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::connect_device', 'ERROR: ('
                            + repr(e) + ')', 4)

    def connect_reply_handler(self):
        try:

            self.holo.dbg_log('bluetooth::connect_reply_handler',
                            'enter_function', 0)

            self.holo.set_busy(0)

            self.menu_connections()

            self.holo.dbg_log('bluetooth::connect_reply_handler',
                            'exit_function', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::connect_reply_handler',
                            'ERROR: (' + repr(e) + ')', 4)

    def disconnect_device(self, listItem=None):
        try:

            self.holo.set_busy(1)

            self.holo.dbg_log('bluetooth::disconnect_device',
                            'enter_function', 0)

            if listItem is None:
                listItem = \
                    self.holo.winHoloMain.getControl(self.holo.listObject['btlist'
                        ]).getSelectedItem()

            if listItem is None:
                return

            device = \
                dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                               , listItem.getProperty('entry')),
                               'org.bluez.Device1')
            device.Disconnect(reply_handler=self.disconnect_reply_handler,
                              error_handler=self.dbus_error_handler)

            self.holo.dbg_log('bluetooth::disconnect_device',
                            'exit_function', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::disconnect_device', 'ERROR: ('
                            + repr(e) + ')', 4)

    def disconnect_reply_handler(self):
        try:

            self.holo.dbg_log('bluetooth::disconnect_reply_handler',
                            'enter_function', 0)

            self.holo.set_busy(0)

            self.menu_connections()

            self.holo.dbg_log('bluetooth::disconnect_reply_handler',
                            'exit_function', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::disconnect_reply_handler',
                            'ERROR: (' + repr(e) + ')', 4)

    def remove_device(self, listItem=None):
        try:

            self.holo.set_busy(1)

            self.holo.dbg_log('bluetooth::remove_device', 'enter_function'
                            , 0)

            if listItem is None:
                listItem = \
                    self.holo.winHoloMain.getControl(self.holo.listObject['btlist'
                        ]).getSelectedItem()

            if listItem is None:
                return

            self.holo.dbg_log('bluetooth::remove_device->entry::',
                            listItem.getProperty('entry'), 0)

            path = listItem.getProperty('entry')
            self.dbusBluezAdapter.RemoveDevice(path)

            self.menu_connections(None)

            self.holo.dbg_log('bluetooth::remove_device', 'exit_function'
                            , 0)

            self.holo.set_busy(0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::remove_device', 'ERROR: ('
                            + repr(e) + ')', 4)


    def start_discovery(self, listItem=None):
        try:

            self.holo.set_busy(1)

            self.holo.dbg_log('bluetooth::start_discovery',
                            'enter_function', 0)

            self.dbusBluezAdapter.StartDiscovery()

            self.holo.set_busy(0)

            self.holo.dbg_log('bluetooth::start_discovery',
                            'exit_function', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::start_discovery', 'ERROR: ('
                            + repr(e) + ')', 4)


    def stop_discovery(self, listItem=None):
        try:

            self.holo.set_busy(1)

            self.holo.dbg_log('bluetooth::stop_discovery',
                            'enter_function', 0)

            self.dbusBluezAdapter.StopDiscovery()

            self.holo.set_busy(0)
            
            self.holo.dbg_log('bluetooth::stop_discovery', 'exit_function'
                            , 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('bluetooth::stop_discovery', 'ERROR: ('
                            + repr(e) + ')', 4)


    def dbus_error_handler(self, error):
        try:

            self.holo.dbg_log('bluetooth::dbus_error_handler',
                            'enter_function', 0)

            self.holo.set_busy(0)

            err_name = error.get_dbus_name()
            xbmc.executebuiltin('Notification(Bluetooth Error, '
                                + err_name.split('.')[-1] + ')')
            self.holo.dbg_log('bluetooth::dbus_error_handler', 'ERROR: ('
                            + err_name + ')', 4)

            self.holo.dbg_log('bluetooth::dbus_error_handler',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::dbus_error_handler', 'ERROR: ('
                            + repr(e) + ')', 4)


    def cleanup_adapter(self):
        try:

            self.holo.dbg_log('bluetooth::cleanup_adapter',
                            'enter_function', 0)
            
            self.dbusBluezAdapter = None

            self.holo.dbg_log('bluetooth::cleanup_adapter',
                            'exit_function', 0)
            
        except Exception, e:

            self.holo.dbg_log('bluetooth::cleanup_adapter', 'ERROR: ('
                            + repr(e) + ')')
            
            
    def init_adapter(self):
        try:

            self.holo.dbg_log('bluetooth::init_adapter',
                            'enter_function', 0)
            
            self.dbusBluezManager = \
                dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                               , '/'),
                               'org.freedesktop.DBus.ObjectManager')
                
            self.dbusBluezAdapter = \
                self.get_adapter()

            if self.dbusBluezAdapter != None:
                self.adapter_powered( \
                  self.dbusBluezAdapter, 1)

            self.holo.dbg_log('bluetooth::init_adapter',
                            'exit_function', 0)
            
        except Exception, e:

            self.holo.dbg_log('bluetooth::init_adapter', 'ERROR: ('
                            + repr(e) + ')')
            
            
    def adapter_powered(self, adapter, state=1):
        try:

            self.holo.dbg_log('bluetooth::adapter_powered',
                            'enter_function', 0)

            if int(self.adapter_info(self.dbusBluezAdapter, 'Powered')) \
                != state:
                self.holo.dbg_log('bluetooth::adapter_powered',
                                'set state (' + str(state) + ')', 0)

                adapter_interface = \
                    dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                                   , adapter.object_path),
                                   'org.freedesktop.DBus.Properties')

                adapter_interface.Set('org.bluez.Adapter1', 'Powered',
                        dbus.Boolean(state))

                del adapter_interface

            self.holo.dbg_log('bluetooth::adapter_powered',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::adapter_powered', 'ERROR: ('
                            + repr(e) + ')', 4)

    def adapter_info(self, adapter, name):
        try:

            self.holo.dbg_log('bluetooth::adapter_info', 'enter_function'
                            , 0)

            adapter_interface = \
                dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                               , adapter.object_path),
                               'org.freedesktop.DBus.Properties')

            self.holo.dbg_log('bluetooth::adapter_info', 'exit_function', 0)

            return adapter_interface.Get('org.bluez.Adapter1', name)
        except Exception, e:

            self.holo.dbg_log('bluetooth::adapter_info', 'ERROR: ('
                            + repr(e) + ')', 4)


 # --------------------------- Bt Monitor Loop Class --------------------------- #

class monitorLoop(threading.Thread):

    def __init__(self, holoMain):
        try:

            holoMain.dbg_log('bluetooth::monitorLoop::__init__',
                           'enter_function', 0)

            self.mainLoop = gobject.MainLoop()

            gobject.threads_init()
            dbus.mainloop.glib.threads_init()

            self.holo = holoMain
            self.dbusSystemBus = holoMain.dbusSystemBus
            self.btAgentPath = '/HoloVisi/bt_agent'

            threading.Thread.__init__(self)

            self.holo.dbg_log('bluetooth::monitorLoop::__init__',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::__init__',
                            'ERROR: (' + repr(e) + ')', 4)


    def run(self):
        try:

            self.holo.dbg_log('bluetooth::monitorLoop::run',
                            'enter_function', 0)

            self.dbusSystemBus.watch_name_owner('org.bluez',
                    self.btNameOwnerChanged)

            try:
                self.holo.dbg_log('Bluetooth Monitor started.', '', 1)
                self.mainLoop.run()
                self.holo.dbg_log('Bluetooth Monitor stopped.', '', 1)
            except:
                pass

            self.holo.dbg_log('bluetooth::monitorLoop::run',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::run', 'ERROR: ('
                            + repr(e) + ')', 4)

    def add_signal_receivers(self):
        try:

            self.holo.dbg_log('bluetooth::monitorLoop::add_signal_receivers',
                            'enter_function', 0)
            
            self.dbusSystemBus.add_signal_receiver(self.InterfacesAdded,
                    bus_name='org.bluez',
                    dbus_interface='org.freedesktop.DBus.ObjectManager'
                    , signal_name='InterfacesAdded')

            self.dbusSystemBus.add_signal_receiver(self.InterfacesRemoved,
                    bus_name='org.bluez',
                    dbus_interface='org.freedesktop.DBus.ObjectManager'
                    , signal_name='InterfacesRemoved')

            self.dbusSystemBus.add_signal_receiver(self.PropertiesChanged,
                    dbus_interface='org.freedesktop.DBus.Properties',
                    signal_name='PropertiesChanged',
                    arg0='org.bluez.Device1', path_keyword='path')     
            
            self.holo.dbg_log('bluetooth::monitorLoop::add_signal_receivers',
                            'exit_function', 0)            
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::add_signal_receivers', 'ERROR: ('
                            + repr(e) + ')', 4)
       
    def remove_signal_receivers(self):
        try:

            self.holo.dbg_log('bluetooth::monitorLoop::remove_signal_receivers',
                            'enter_function', 0)   
            
            self.dbusSystemBus.remove_signal_receiver(self.InterfacesAdded,
                    bus_name='org.bluez',
                    dbus_interface='org.freedesktop.DBus.ObjectManager'
                    , signal_name='InterfacesAdded')

            self.dbusSystemBus.remove_signal_receiver(self.InterfacesRemoved,
                    bus_name='org.bluez',
                    dbus_interface='org.freedesktop.DBus.ObjectManager'
                    , signal_name='InterfacesRemoved')

            self.dbusSystemBus.remove_signal_receiver(self.PropertiesChanged,
                    dbus_interface='org.freedesktop.DBus.Properties',
                    signal_name='PropertiesChanged',
                    arg0='org.bluez.Device1', path_keyword='path')   
            
            self.holo.dbg_log('bluetooth::monitorLoop::remove_signal_receivers',
                            'exit_function', 0)               
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::remove_signal_receivers', 'ERROR: ('
                            + repr(e) + ')', 4)
 
           
    def exit(self):
        try:

            self.holo.dbg_log('bluetooth::monitorLoop::exit',
                            'enter_function', 0)

            self.initialize_agent(False)
            self.mainLoop.quit()
                              
            self.holo.dbg_log('bluetooth::monitorLoop::exit',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::quit', 'ERROR: ('
                            + repr(e) + ')', 4)


    def btNameOwnerChanged(self, proxy):
        try:

            self.holo.dbg_log('bluetooth::monitorLoop::nameOwnerChanged',
                            'enter_function', 0)
          
            if proxy:
                self.bt_available = True
                test_adapter_count = 0
                
                if not self.holo.read_setting('system', 'disable_bt') == '1':
                    
                    #wait max. 10 sec for an Adapter
                    while self.holo.dictModules['bluetooth'].dbusBluezAdapter == None and \
                      test_adapter_count < 3:
                    
                        self.holo.dictModules['bluetooth'].init_adapter()
                        test_adapter_count = test_adapter_count + 1
                    
                        if self.holo.dictModules['bluetooth'].dbusBluezAdapter == None:
                            time.sleep(1)
                            
                if self.holo.dictModules['bluetooth'].active:
                    self.initialize_agent()
            else:
            
                self.bt_available = False
                
                if self.holo.dictModules['bluetooth'].active:
                    self.initialize_agent()                
                
            self.holo.dbg_log('bluetooth::monitorLoop::nameOwnerChanged',
                            'exit_function', 0)                
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::nameOwnerChanged',
                            'ERROR: (' + repr(e) + ')', 4)
            
            
    def initialize_agent(self, state=True):
        try:

            self.holo.dbg_log('bluetooth::monitorLoop::initialize_agent',
                            'enter_function', 0)

            if self.bt_available == True and state == True:

                self.holo.dbg_log('bluetooth::monitorLoop::initialize_agent'
                                , 'btAgent is connected to system bus', 0)

                self.dbusBluezManager = \
                    dbus.Interface(self.dbusSystemBus.get_object('org.bluez'
                        , '/org/bluez'), 'org.bluez.AgentManager1')
                        
                self.btAgent = bluetoothAgent(self.dbusSystemBus, self.btAgentPath)
                self.btAgent.holo = self.holo
                self.btAgent.dbusSystemBus = self.dbusSystemBus

                self.dbusBluezManager.RegisterAgent(self.btAgentPath, 'KeyboardDisplay')
                self.dbusBluezManager.RequestDefaultAgent(self.btAgentPath)
                
                self.add_signal_receivers()
               
            else:

                self.holo.dbg_log('bluetooth::monitorLoop::initialize_agent'
                                ,
                                'btAgent is disconnected from system bus'
                                , 0)

                self.remove_signal_receivers()
                
                if hasattr(self, 'btAgent'):
                    if self.bt_available == True:
                        self.dbusBluezManager.UnregisterAgent(self.btAgentPath)

                    self.btAgent.remove_from_connection(self.dbusSystemBus,
                            self.btAgentPath)
                    self.btAgent = None
                    del self.btAgent

                if hasattr('self', 'dbusBluezManager'):
                    self.dbusBluezManager = None
                    del self.dbusBluezManager
                 
            self.holo.dbg_log('bluetooth::monitorLoop::initialize_agent',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::initialize_agent',
                            'ERROR: (' + repr(e) + ')', 4)

    def InterfacesAdded(self, path, interfaces):

        if self.bt_available == False:
            return

        if not path in self.holo.dictModules['bluetooth'].listItems:
            return
            
        self.holo.dbg_log('bluetooth::monitorLoop::InterfacesAdded',
                        'enter_function', 4)
        self.holo.dictModules['bluetooth'].menu_connections()
        self.holo.dbg_log('bluetooth::monitorLoop::InterfacesAdded',
                        'exit_function', 4)

    def InterfacesRemoved(self, path, interfaces):

        if self.bt_available == False:
            return

        if not path in self.holo.dictModules['bluetooth'].listItems:
            return
            
        self.holo.dbg_log('bluetooth::monitorLoop::InterfacesRemoved',
                        'enter_function', 4)
        self.holo.dictModules['bluetooth'].menu_connections()
        self.holo.dbg_log('bluetooth::monitorLoop::InterfacesRemoved',
                        'exit_function', 4)

    def PropertiesChanged(
        self,
        interface,
        changed,
        invalidated,
        path,
        ):
        try:


            if self.bt_available == False:
                return

            if not path in self.holo.dictModules['bluetooth'].listItems:
                return
              
            self.holo.dbg_log('bluetooth::monitorLoop::PropertiesChanged'
                            , 'enter_function', 4)

            names = ['Connected', 'Trusted', 'Paired']
            for name in names:
                if name in changed:

                    if name == 'Connected':
                        if changed[name]:
                            self.holo.dictModules['bluetooth'
                                    ].listItems[path].setProperty('ConnectedState'
                                    , self.holo._(32333) + '[COLOR white]'
                                     + self.holo._(32334) + '[/COLOR]')
                        else:
                            self.holo.dictModules['bluetooth'
                                    ].listItems[path].setProperty('ConnectedState'
                                    , self.holo._(32333) + '[COLOR white]'
                                     + self.holo._(32335) + '[/COLOR]')

                    self.holo.dictModules['bluetooth'
                            ].listItems[path].setProperty(name,
                            str(changed[name]))
                    self.holo.dictModules['bluetooth'].menu_connections()
                    self.forceRender()

            self.holo.dbg_log('bluetooth::monitorLoop::PropertiesChanged'
                            , 'exit_function', 4)
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::PropertiesChanged'
                            , 'ERROR: (' + repr(e) + ')', 4)

    def forceRender(self):
        try:

            self.holo.dbg_log('bluetooth::monitorLoop::forceRender',
                            'enter_function', 0)

            focusId = self.holo.winHoloMain.getFocusId()
            self.holo.winHoloMain.setFocusId(self.holo.listObject['btlist'])
            self.holo.winHoloMain.setFocusId(focusId)

            self.holo.dbg_log('bluetooth::monitorLoop::forceRender',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::monitorLoop::forceRender',
                            'ERROR: (' + repr(e) + ')', 4)


class Rejected(dbus.DBusException):

    _dbus_error_name = 'org.bluez.Error.Rejected'


class bluetoothAgent(dbus.service.Object):

    exit_on_release = True

    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release

    def busy(self):

        self.holo.input_request = False
        if self.holo.__busy__ > 0:
            xbmc.executebuiltin('ActivateWindow(busydialog)')

    def set_trusted(self, path):
        try:

            props = \
                dbus.Interface(self.holo.dbusSystemBus.get_object('org.bluez'
                               , path),
                               'org.freedesktop.DBus.Properties')

            props.Set('org.bluez.Device1', 'Trusted', True)
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::display_passkey_window'
                            , 'ERROR: (' + repr(e) + ')', 4)

    def show_passkey_window(self, requested):
        try:

            self.passkey_window = \
                holoWindows.passkeyWindow('getPasskey.xml',
                    self.holo.__cwd__, 'Default', holoMain=self.holo)
            self.passkey_window.show()
            self.passkey_window.set_text(self.holo._(32343))
            self.passkey_window.set_requested_code(requested)

            self.passkey_timer = passkeyTimer(self.holo, self)
            self.passkey_timer.start()
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::display_passkey_window'
                            , 'ERROR: (' + repr(e) + ')', 4)

    def close_passkey_window(self):

        try:

            if self.passkey_timer.stopped == False:
                self.passkey_timer.stop()
                del self.passkey_timer

            if hasattr(self, 'passkey_window'):
                self.passkey_window.close()
                del self.passkey_window
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::display_passkey_window'
                            , 'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='',
                         out_signature='')
    def Release(self):
        pass

    @dbus.service.method('org.bluez.Agent1', in_signature='os',
                         out_signature='')
    def AuthorizeService(self, device, uuid):
        try:
            self.holo.dbg_log('bluetooth::btAgent::AuthorizeService',
                            'enter_function', 0)

            self.holo.input_request = True
            xbmc.executebuiltin('Dialog.Close(busydialog)')

            self.holo.dbg_log('bluetooth::btAgent::AuthorizeService::device='
                            , device, 0)
            self.holo.dbg_log('bluetooth::btAgent::AuthorizeService::uuid='
                            , uuid, 0)

            self.holo.dbg_log('bluetooth::btAgent::AuthorizeService',
                            'enter_function', 0)

            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.yesno('HoloVisi Bluetooth',
                    'AuthorizeService')

            if answer == 1:
                self.holo.dictModules['bluetooth'].trust_device(device)
                return

            raise Rejected('Connection rejected by user')
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::AuthorizeService',
                            'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='o',
                         out_signature='s')
    def RequestPinCode(self, device):
        try:

            self.holo.dbg_log('bluetooth::btAgent::RequestPinCode',
                            'enter_function', 0)

            self.holo.input_request = True
            xbmc.executebuiltin('Dialog.Close(busydialog)')

            self.holo.dbg_log('bluetooth::btAgent::RequestPinCode::device='
                            , device, 0)

            xbmcKeyboard = xbmc.Keyboard('', 'RequestPinCode')
            xbmcKeyboard.doModal()
            pincode = xbmcKeyboard.getText()
            self.holo.dbg_log('bluetooth::btAgent::RequestPinCode',
                            'return->' + pincode, 0)
            self.holo.dbg_log('bluetooth::btAgent::RequestPinCode',
                            'exit_function', 0)
            return pincode
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::RequestPinCode',
                            'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='o',
                         out_signature='u')
    def RequestPasskey(self, device):
        try:

            self.holo.dbg_log('bluetooth::btAgent::RequestPasskey',
                            'enter_function', 0)

            self.holo.input_request = True
            xbmc.executebuiltin('Dialog.Close(busydialog)')

            self.holo.dbg_log('bluetooth::btAgent::RequestPasskey::device='
                            , device, 0)

            xbmcKeyboard = xbmc.Keyboard('', 'RequestPasskey')
            xbmcKeyboard.doModal()

            passkey = xbmcKeyboard.getText()
            self.holo.dbg_log('bluetooth::btAgent::RequestPasskey',
                            'return->' + passkey, 0)
            self.holo.dbg_log('bluetooth::btAgent::RequestPasskey',
                            'exit_function', 0)
            return dbus.UInt32(passkey)
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::RequestPasskey',
                            'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='ouq',
                         out_signature='')
    def DisplayPasskey(
        self,
        device,
        passkey,
        entered,
        ):
        try:

            self.holo.dbg_log('bluetooth::btAgent::DisplayPasskey',
                            'enter_function', 0)

            self.holo.dbg_log('bluetooth::btAgent::DisplayPasskey::device='
                            , repr(device), 0)
            self.holo.dbg_log('bluetooth::btAgent::DisplayPasskey::passkey='
                            , repr(passkey), 0)
            self.holo.dbg_log('bluetooth::btAgent::DisplayPasskey::entered='
                            , repr(entered), 0)

            if not hasattr(self, 'passkey_window'):
                self.show_passkey_window(passkey)
            else:

                self.passkey_window.update_entered_code(entered)

            if len(self.passkey_window.get_entered_code()) \
                == len(str(passkey)):
                self.close_passkey_window()

            self.holo.dbg_log('bluetooth::btAgent::DisplayPasskey',
                            'enter_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::DisplayPasskey',
                            'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='os',
                         out_signature='')
    def DisplayPinCode(self, device, pincode):
        try:

            self.holo.dbg_log('bluetooth::btAgent::DisplayPinCode',
                            'enter_function', 0)

            self.holo.dbg_log('bluetooth::btAgent::DisplayPinCode::device='
                            , repr(device), 0)
            self.holo.dbg_log('bluetooth::btAgent::DisplayPinCode::pincode='
                            , repr(pincode), 0)

            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.ok('HoloVisi Bluetooth',
                                   'DisplayPasskey', str(pincode))

            self.holo.dbg_log('bluetooth::btAgent::DisplayPinCode',
                            'enter_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::DisplayPinCode',
                            'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='ou',
                         out_signature='')
    def RequestConfirmation(self, device, passkey):
        try:

            self.holo.dbg_log('bluetooth::btAgent::RequestConfirmation',
                            'enter_function', 0)

            self.holo.dbg_log('bluetooth::btAgent::RequestConfirmation::device='
                            , device, 0)
            self.holo.dbg_log('bluetooth::btAgent::RequestConfirmation::passkey='
                            , repr(passkey), 0)

            self.holo.dbg_log('bluetooth::btAgent::RequestConfirmation',
                            'enter_function', 0)

            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.yesno('HoloVisi Bluetooth',
                    'RequestConfirmation', str(passkey))

            self.holo.dbg_log('bluetooth::btAgent::RequestConfirmation::answer='
                            , repr(answer), 0)

            if answer == 1:
                self.holo.dictModules['bluetooth'].trust_device(device)
                return

            raise Rejected("Passkey doesn't match")

        except Exception, e:
            self.holo.dbg_log('bluetooth::btAgent::RequestConfirmation', 'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='o', out_signature='')
    def RequestAuthorization(self, device):
        try:

            self.holo.dbg_log('bluetooth::btAgent::RequestAuthorization',
                            'enter_function', 0)

            self.holo.dbg_log('bluetooth::btAgent::RequestAuthorization::device='
                            , device, 0)

            self.holo.dbg_log('bluetooth::btAgent::RequestAuthorization',
                            'enter_function', 0)

            xbmcDialog = xbmcgui.Dialog()
            answer = xbmcDialog.yesno('HoloVisi Bluetooth',
                    'RequestAuthorization')

            if answer == 1:
                return

            raise Rejected('Pairing rejected')
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::RequestAuthorization',
                            'ERROR: (' + repr(e) + ')', 4)

    @dbus.service.method('org.bluez.Agent1', in_signature='',
                         out_signature='')
    def Cancel(self):
        try:

            self.holo.dbg_log('bluetooth::btAgent::Cancel',
                            'enter_function', 0)
            self.holo.dbg_log('bluetooth::btAgent::Cancel',
                            'enter_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::btAgent::Cancel', 'ERROR: ('
                            + repr(e) + ')', 4)


class discoveryThread(threading.Thread):

    def __init__(self, holoMain):
        try:

            holoMain.dbg_log('bluetooth::discoveryThread::__init__',
                           'enter_function', 0)

            self.holo = holoMain
            self.last_run = 0
            self.stopped = False
            self.main_menu = \
                self.holo.winHoloMain.getControl(self.holo.winHoloMain.guiMenList)

            threading.Thread.__init__(self)

            self.holo.dbg_log('bluetooth::discoveryThread::__init__',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::discoveryThread::__init__',
                            'ERROR: (' + repr(e) + ')')

    def stop(self):

        self.stopped = True
        self.holo.dictModules['bluetooth'].stop_discovery()

    def run(self):
        try:

            self.holo.dbg_log('bluetooth::discoveryThread::run',
                            'enter_function', 0)

            while not self.stopped and not xbmc.abortRequested:

                current_time = time.time()
                if current_time > self.last_run + 5:
                    self.holo.dictModules['bluetooth'
                            ].menu_connections(None)
                    self.last_run = current_time

                if not self.main_menu.getSelectedItem().getProperty('modul'
                        ) == 'bluetooth':
                    self.stop()

                time.sleep(1)
                
            self.holo.dbg_log('bluetooth::discoveryThread', 'Stopped', 1)

            self.holo.dbg_log('bluetooth::discoveryThread::run',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::discoveryThread::run', 'ERROR: ('
                            + repr(e) + ')')


class passkeyTimer(threading.Thread):

    def __init__(self, holoMain, agent):
        try:

            holoMain.dbg_log('bluetooth::passkeyTimer::__init__',
                           'enter_function', 0)

            self.holo = holoMain
            self.agent = agent
            self.start_time = time.time()
            self.last_run = time.time()
            self.stopped = False
            self.runtime = 60

            threading.Thread.__init__(self)

            self.holo.dbg_log('bluetooth::passkeyTimer', 'Started', 1)

            self.holo.dbg_log('bluetooth::passkeyTimer::__init__',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::passkeyTimer::__init__', 'ERROR: ('
                             + repr(e) + ')')

    def stop(self):

        self.stopped = True

    def run(self):
        try:

            self.holo.dbg_log('bluetooth::passkeyTimer::run',
                            'enter_function', 0)

            while not self.stopped and not xbmc.abortRequested:

                current_time = time.time()

                percent = round(100 / self.runtime * (self.start_time
                                + self.runtime - current_time))
                self.agent.passkey_window.getControl(1703).setPercent(percent)

                if current_time > self.start_time + self.runtime:
                    self.agent.close_passkey_window()
                    self.stopped = True
                else:
                    time.sleep(1)

            self.holo.dbg_log('bluetooth::passkeyTimer', 'Stopped', 1)

            self.holo.dbg_log('bluetooth::passkeyTimer::run', 'exit_function'
                            , 0)
        except Exception, e:

            self.holo.dbg_log('bluetooth::passkeyTimer::run', 'ERROR: ('
                            + repr(e) + ')')

# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import os
import time
import re
from xml.dom import minidom
from threading import Thread


class mainWindow(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):

        self.lastMenu = -1
        self.lastEntry = -1

        self.guiMenList = 1000
        self.guiList = 1100
        self.guiNetList = 1200
        self.guiBtList = 1300
        self.guiOther = 1900

        self.guiLists = [1000, 1100, 1200, 1300]

        self.buttons = {
            1: {'id': 1500, 'modul': '', 'action': ''},
            2: {'id': 1501, 'modul': '', 'action': ''},
            3: {'id': 1502, 'modul': '', 'action': ''},
            4: {'id': 1503, 'modul': '', 'action': ''},
            5: {'id': 1504, 'modul': '', 'action': ''},
            }

        self.isChild = False
        self.holo = kwargs['holoMain']
        self.lastGuiList = -1

        if 'isChild' in kwargs:
            self.isChild = True

        pass

    def onInit(self):
        try:

            if self.isChild:
                self.setFocusId(self.guiMenList)
                self.onFocus(self.guiMenList)
                return

            self.holo.set_busy(1)

            self.holo.winHoloMain = self

            for strModule in sorted(self.holo.dictModules,
                                    key=lambda x: self.holo.dictModules[x].menu.keys()):

                # self.holo.dbg_log('init module', strModule, 0)
                self.holo.dbg_log('init module', strModule)

                if hasattr(self.holo.dictModules[strModule], 'do_init'):
                    Thread(target=self.holo.dictModules[strModule].do_init(), args=()).start()

                for men in self.holo.dictModules[strModule].menu:
                    dictProperties = {'modul': strModule,
                                      'listTyp':
                                          self.holo.listObject[self.holo.dictModules[strModule].menu[men]['listTyp']],
                                      'menuLoader': self.holo.dictModules[strModule].menu[men]['menuLoader']}

                    if 'InfoText' in self.holo.dictModules[strModule].menu[men]:
                        dictProperties['InfoText'] = \
                            self.holo._(self.holo.dictModules[strModule].menu[men]['InfoText'])

                    self.addMenuItem(self.holo.dictModules[strModule].menu[men]['name'], dictProperties)

            self.setFocusId(self.guiMenList)
            self.onFocus(self.guiMenList)

            self.holo.set_busy(0)
            
        except Exception, e:
            self.holo.set_busy(0)
            self.holo.dbg_log('holoWindows.mainWindow::onInit', 'ERROR: (' + repr(e) + ')')

    def addMenuItem(self, strName, dictProperties):

        try:

            lstItem = xbmcgui.ListItem(label=self.holo._(strName))

            for strProp in dictProperties:
                lstItem.setProperty(strProp,
                                    str(dictProperties[strProp]))

            self.getControl(self.guiMenList).addItem(lstItem)
        
        except Exception, e:
            self.holo.dbg_log('holoWindows.mainWindow::addMenuItem(' + str(strName) + ')',
                              'ERROR: (' + repr(e) + ')')

    def addConfigItem(
        self,
        strName,
        dictProperties,
        strType,):

        try:

            lstItem = xbmcgui.ListItem(label=strName)

            for strProp in dictProperties:
                lstItem.setProperty(strProp,
                                    str(dictProperties[strProp]))

            self.getControl(int(strType)).addItem(lstItem)

            return lstItem

        except Exception, e:
            self.holo.dbg_log('holoWindows.mainWindow::addConfigItem(' + strName + ')',
                              'ERROR: (' + repr(e) + ')')

    def showButton(
        self,
        number,
        name,
        module,
        action,
        onup=None,
        onleft=None,):
        try:

            self.holo.dbg_log('holoWindows::showButton', 'enter_function',
                            0)

            button = self.getControl(self.buttons[number]['id'])
            self.buttons[number]['modul'] = module
            self.buttons[number]['action'] = action
            button.setLabel(self.holo._(name))

            if onup != None:
                button.controlUp(self.getControl(onup))

            if onleft != None:
                button.controlLeft(self.getControl(onleft))

            button.setVisible(True)

            self.holo.dbg_log('holoWindows::showButton', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('holoWindows.mainWindow::showButton('
                            + str(number) + ', ' + str(action) + ')',
                            'ERROR: (' + repr(e) + ')')

    def onAction(self, action):

        try:

            focusId = self.getFocusId()
            actionId = int(action.getId())

            if focusId == 2222:
                if actionId == 61453:
                    return

            if actionId in self.holo.CANCEL:
                self.close()

            if focusId == self.guiList:

                curPos = self.getControl(focusId).getSelectedPosition()
                listSize = self.getControl(focusId).size()
                newPos = curPos
                nextItem = self.getControl(focusId).getListItem(newPos)

                if (curPos != self.lastGuiList
                    or nextItem.getProperty('typ') == 'separator') \
                    and actionId in [2, 3, 4]:

                    while nextItem.getProperty('typ') == 'separator':

                        if actionId == 2:
                            newPos = newPos + 1

                        if actionId == 3:
                            newPos = newPos - 1

                        if actionId == 4:
                            newPos = newPos + 1

                        if newPos <= 0:
                            newPos = listSize - 1

                        if newPos >= listSize:
                            newPos = 0

                        nextItem = \
                            self.getControl(focusId).getListItem(newPos)

                    self.lastGuiList = newPos
                    self.getControl(focusId).selectItem(newPos)

                    self.setProperty('InfoText',
                            nextItem.getProperty('InfoText'))

            if focusId == self.guiMenList:
                self.setFocusId(focusId)
        except Exception, e:

            self.holo.dbg_log('holoWindows.mainWindow::onAction('
                            + str(action) + ')', 'ERROR: (' + repr(e)
                            + ')')
            if actionId in self.holo.CANCEL:
                self.close()

    def onClick(self, controlID):

        self.holo.dbg_log('holoWindows::onClick', 'enter_function', 0)

        try:

            for btn in self.buttons:
                if controlID == self.buttons[btn]['id']:
                    modul = self.buttons[btn]['modul']
                    action = self.buttons[btn]['action']
                    if hasattr(self.holo.dictModules[modul], action):
                        if getattr(self.holo.dictModules[modul],
                                   action)() == 'close':
                            self.close()
                        return

            if controlID in self.guiLists:
                selectedPosition = \
                    self.getControl(controlID).getSelectedPosition()
                selectedMenuItem = \
                    self.getControl(self.guiMenList).getSelectedItem()
                selectedItem = \
                    self.getControl(controlID).getSelectedItem()
                strTyp = selectedItem.getProperty('typ')
                strValue = selectedItem.getProperty('value')

                if strTyp == 'multivalue':
                    select_window = selectWindow('selectWindow.xml',
                            self.holo.__cwd__, 'Default', holoMain=self.holo)
                    select_window.defaultValue = strValue
                    select_window.availValues = \
                        selectedItem.getProperty('values')
                    select_window.doModal()
                    selectedItem.setProperty('value',
                            select_window.result)
                    del select_window
                elif strTyp == 'text':

                    xbmcKeyboard = xbmc.Keyboard(strValue)
                    result_is_valid = False
                    while not result_is_valid:
                        xbmcKeyboard.doModal()

                        if xbmcKeyboard.isConfirmed():
                            result_is_valid = True
                            validate_string = \
                                selectedItem.getProperty('validate')
                            if validate_string != '':
                                if not re.search(validate_string,
                                        xbmcKeyboard.getText()):
                                    result_is_valid = False
                        else:
                            result_is_valid = True

                    if xbmcKeyboard.isConfirmed():
                        selectedItem.setProperty('value',
                                xbmcKeyboard.getText())
                elif strTyp == 'file':

                    xbmcDialog = xbmcgui.Dialog()
                    returnValue = xbmcDialog.browse(
                        1,
                        'HoloVisi.com',
                        'files',
                        '',
                        False,
                        False,
                        '/',
                        )
                    if returnValue != '' and returnValue != '/':
                        selectedItem.setProperty('value',
                                str(returnValue))
                elif strTyp == 'ip':

                    xbmcDialog = xbmcgui.Dialog()
                    returnValue = xbmcDialog.numeric(3, 'HoloVisi.com',
                            strValue)
                    if returnValue != '':
                        if returnValue == '0.0.0.0':
                            selectedItem.setProperty('value', '')
                        else:
                            selectedItem.setProperty('value',
                                    returnValue)
                elif strTyp == 'num':

                    if strValue == 'None' or strValue == '':
                        strValue = '0'

                    xbmcDialog = xbmcgui.Dialog()
                    returnValue = xbmcDialog.numeric(0, 'HoloVisi.com',
                            strValue)
                    if returnValue == '':
                        returnValue = -1

                    if returnValue > -1:
                        selectedItem.setProperty('value',
                                str(returnValue))
                elif strTyp == 'bool':

                    if strValue == '0':
                        selectedItem.setProperty('value', '1')
                    else:
                        selectedItem.setProperty('value', '0')

                if selectedItem.getProperty('action') != '':
                    if hasattr(self.holo.dictModules[selectedMenuItem.getProperty('modul'
                               )], selectedItem.getProperty('action')):
                        getattr(self.holo.dictModules[selectedMenuItem.getProperty('modul'
                                )], selectedItem.getProperty('action'
                                ))(listItem=selectedItem)
                        self.emptyButtonLabels()

                self.lastMenu = -1
                self.onFocus(self.guiMenList)

                self.setFocusId(controlID)
                self.getControl(controlID).selectItem(selectedPosition)

            self.holo.dbg_log('holoWindows::onClick', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('holoWindows.mainWindow::onClick('
                            + str(controlID) + ')', 'ERROR: ('
                            + repr(e) + ')')

    def onFocus(self, controlID):

        try:

            if controlID in self.guiLists:

                currentEntry = \
                    self.getControl(controlID).getSelectedPosition()

                selectedEntry = \
                    self.getControl(controlID).getSelectedItem()
                if controlID == self.guiList:
                    self.setProperty('InfoText',
                            selectedEntry.getProperty('InfoText'))

                if currentEntry != self.lastGuiList:

                    self.lastGuiList = currentEntry

                    if selectedEntry is not None:
                        strHoover = \
                            selectedEntry.getProperty('hooverValidate')

                        if strHoover != '':
                            if hasattr(self.holo.dictModules[selectedEntry.getProperty('modul'
                                    )], strHoover):
                                self.emptyButtonLabels()
                                getattr(self.holo.dictModules[selectedEntry.getProperty('modul'
                                        )], strHoover)(selectedEntry)

            if controlID == self.guiMenList:

                lastMenu = \
                    self.getControl(controlID).getSelectedPosition()

                selectedMenuItem = \
                    self.getControl(controlID).getSelectedItem()
                self.setProperty('InfoText',
                                 selectedMenuItem.getProperty('InfoText'
                                 ))

                if lastMenu != self.lastMenu:

                    self.lastMenu = lastMenu

                    for btn in self.buttons:
                        self.getControl(self.buttons[btn]['id'
                                ]).setVisible(False)

                    strMenuLoader = \
                        selectedMenuItem.getProperty('menuLoader')

                    self.getControl(self.guiList).reset()

                    if int(selectedMenuItem.getProperty('listTyp')) \
                        == self.guiOther:
                        self.getControl(controlID).controlRight(self.getControl(self.buttons[1]['id'
                                ]))
                    else:
                        objList = \
                            self.getControl(int(selectedMenuItem.getProperty('listTyp'
                                )))
                        self.getControl(controlID).controlRight(objList)

                    if strMenuLoader != '':
                        if hasattr(self.holo.dictModules[selectedMenuItem.getProperty('modul'
                                   )], strMenuLoader):
                            getattr(self.holo.dictModules[selectedMenuItem.getProperty('modul'
                                    )], strMenuLoader)(selectedMenuItem)
        except Exception, e:

            self.holo.dbg_log('holoWindows.mainWindow::onFocus('
                            + str(controlID) + ')', 'ERROR: ('
                            + repr(e) + ')')

    def emptyButtonLabels(self):
        for btn in self.buttons:

      # if self.buttons[btn]['action'] == '':

            self.getControl(self.buttons[btn]['id']).setVisible(False)


class selectWindow(xbmcgui.WindowXMLDialog):

    listId = 2000
    defaultValue = None

    availValues = []

    def __init__(self, *args, **kwargs):
        self.holo = kwargs['holoMain']
        pass

    def onInit(self):

        self.getControl(self.listId).reset()

        for strValue in self.availValues.split(','):
            if strValue != '':
                strValueS = strValue.split(':')
                if len(strValueS) > 1:
                    listItem = \
                        xbmcgui.ListItem(label=strValueS[0].strip(),
                            label2=strValueS[1].strip())
                else:
                    listItem = xbmcgui.ListItem(label=strValue,
                            label2=strValue)

                self.getControl(self.listId).addItem(listItem)

        for x in range(0, self.getControl(self.listId).size()):
            if self.getControl(self.listId).getListItem(x).getLabel() \
                == self.defaultValue:
                self.getControl(self.listId).selectItem(x)

        self.result = self.defaultValue

        self.setFocusId(self.listId)

    def onAction(self, action):
        actionId = int(action.getId())
        if actionId in self.holo.CANCEL:
            self.close()

    def onClick(self, controlID):
        selectedItem = self.getControl(self.listId).getSelectedItem()
        self.result = selectedItem.getLabel()
        self.close()

    def onFocus(self, controlID):
        pass


class passkeyWindow(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        self.holo = kwargs['holoMain']
        pass

    def set_text(self, text):
        self.getControl(1700).setLabel(text)

    def set_requested_code(self, requested):
        self.getControl(1701).setLabel(str(requested))

    def update_entered_code(self, entered):
        code = self.getControl(1702).getLabel()
        self.getControl(1702).setLabel(code + str(entered))

    def get_entered_code(self):
        return self.getControl(1702).getLabel()

    def onInit(self):
        pass

    def onAction(self, action):
        pass

    def onClick(self, controlID):
        pass

    def onFocus(self, controlID):
        pass


class contextWindow(xbmcgui.WindowXMLDialog):

    groupId = 1998
    imageId = 1999
    listId = 4323

    def __init__(self, *args, **kwargs):

        try:

            self.holo = kwargs['holoMain']

            self.count = 0
            self.options = {}
            self.result = ''
        except Exception, e:

            self.holo.dbg_log('holoWindows.contextWindow::__init__()',
                            'ERROR: (' + repr(e) + ')')

    def onInit(self):

        try:

            self.holo.dbg_log('holoWindows.contextWindow.onInit',
                            'enter_function', 0)

            self.result = ''
            self.count = len(self.options)

            self.getControl(self.imageId).setHeight(self.count * 40
                    + 34)

            if self.count < 4:
                top = round(self.count / 2) * 40
                self.getControl(self.groupId).setPosition(0, int(top))

            if self.count > 4:
                top = round((self.count - 4) / 2) * 40
                self.getControl(self.groupId).setPosition(0, -int(top))

            self.getControl(self.listId).reset()
            for option in sorted(self.options, key=lambda x: \
                                 self.options):
                listItem = \
                    xbmcgui.ListItem(label=self.options[option]['text'])
                listItem.setProperty('id', str(option))
                listItem.setProperty('action',
                        self.options[option]['action'])
                self.getControl(self.listId).addItem(listItem)

            self.setFocusId(self.listId)

            self.holo.dbg_log('holoWindows.contextWindow.onInit', 'exit_function', 0)
            
        except Exception, e:
            self.holo.dbg_log('holoWindows.contextWindow::onInit()', 'ERROR: (' + repr(e) + ')')

    def onAction(self, action):
        try:

            actionId = int(action.getId())
            if actionId in self.holo.CANCEL:
                self.options = {}
                self.close()

        except Exception, e:
            self.holo.dbg_log('holoWindows.contextWindow::onInit()', 'ERROR: (' + repr(e) + ')')

    def onClick(self, controlID):
        try:

            selectedItem = \
                self.getControl(self.listId).getSelectedItem()
            self.result = self.options[int(selectedItem.getProperty('id'
                    ))]['action']
            self.options = {}
            self.close()

        except Exception, e:
            self.holo.dbg_log('holoWindows.contextWindow::onInit()', 'ERROR: (' + repr(e) + ')')

    def onFocus(self, controlID):
        pass


class wizard(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):

        self.guiMenList = 1000
        self.guiNetList = 1200
        self.wizTextbox = 1400
        self.wizTitle = 1399
        self.wizBtnTitle = 1403
        self.wizLstTitle = 1404
        self.wizWinTitle = 32300

        self.guisettings = '/storage/.xbmc/userdata/guisettings.xml'
        self.languages_dir = '/usr/share/xbmc/language/'

        self.holo = kwargs['holoMain']

        self.buttons = {
            1: {'id': 1500, 'modul': '', 'action': ''},
            2: {'id': 1501, 'modul': '', 'action': ''},
            3: {'id': 1401, 'modul': '', 'action': ''},
            4: {'id': 1402, 'modul': '', 'action': ''},
            }

        self.radiobuttons = {1: {'id': 1406, 'modul': '',
                             'action': ''}, 2: {'id': 1407,
                             'modul': '', 'action': ''}}

        self.actions = {}

        self.wizards = []
        self.last_wizard = None

    def onInit(self):
        try:

            self.holo.dictModules['system'].start_service()
            self.holo.dictModules['system'].do_init()

            self.getControl(self.wizWinTitle).setLabel(self.holo._(32300))
            self.getControl(self.buttons[3]['id']).setVisible(False)
            self.getControl(self.buttons[4]['id']).setVisible(False)
            self.getControl(self.radiobuttons[1]['id'
                            ]).setVisible(False)
            self.getControl(self.radiobuttons[2]['id'
                            ]).setVisible(False)

            self.set_wizard_title(self.holo._(32301))
            self.set_wizard_text(self.holo._(32302))
            self.set_wizard_button_title(self.holo._(32307))
            self.set_wizard_button_1(self.get_current_language(), self,
                    'select_language')

            if self.holo.dictModules['system'].keyboard_layouts == True:
                self.set_wizard_button_2(self.holo._(32310)
                        + self.get_keyboard_layout(), self,
                        'select_keyboard')

            self.showButton(1, 32303)

            self.setFocusId(self.buttons[1]['id'])

        except Exception, e:
            self.holo.dbg_log('holoWindows.wizard::onInit()', 'ERROR: (' + repr(e) + ')')

    def set_wizard_text(self, text):
        try:

            self.getControl(self.wizTextbox).setText(text)
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_wizard_text()',
                            'ERROR: (' + repr(e) + ')')

    def set_wizard_title(self, title):
        try:

            self.getControl(self.wizTitle).setLabel(title)
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_wizard_title()',
                            'ERROR: (' + repr(e) + ')')

    def set_wizard_button_title(self, title):
        try:

            self.getControl(self.wizBtnTitle).setLabel(title)

        except Exception, e:
            self.holo.dbg_log('holoWindows.wizard::set_wizard_button_title()'
                            , 'ERROR: (' + repr(e) + ')')

    def set_wizard_list_title(self, title):
        try:

            self.getControl(self.wizLstTitle).setLabel(title)
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_wizard_list_title()'
                            , 'ERROR: (' + repr(e) + ')')

    def set_wizard_button_1(
        self,
        label,
        modul,
        action,
        ):
        try:

            self.buttons[3]['modul'] = modul
            self.buttons[3]['action'] = action
            self.getControl(self.buttons[3]['id']).setLabel(label)
            self.getControl(self.buttons[3]['id']).setVisible(True)

            self.getControl(self.buttons[3]['id'
                            ]).controlRight(self.getControl(self.buttons[1]['id'
                    ]))
            self.getControl(self.buttons[3]['id'
                            ]).controlDown(self.getControl(self.buttons[1]['id'
                    ]))

            self.getControl(self.buttons[1]['id'
                            ]).controlUp(self.getControl(self.buttons[3]['id'
                    ]))
            self.getControl(self.buttons[1]['id'
                            ]).controlLeft(self.getControl(self.buttons[3]['id'
                    ]))
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_wizard_button_1()',
                            'ERROR: (' + repr(e) + ')')

    def set_wizard_button_2(
        self,
        label,
        modul,
        action,
        ):
        try:

            self.buttons[4]['modul'] = modul
            self.buttons[4]['action'] = action
            self.getControl(self.buttons[4]['id']).setLabel(label)
            self.getControl(self.buttons[4]['id']).setVisible(True)

            self.getControl(self.buttons[4]['id'
                            ]).controlLeft(self.getControl(self.buttons[3]['id'
                    ]))
            self.getControl(self.buttons[4]['id'
                            ]).controlDown(self.getControl(self.buttons[1]['id'
                    ]))
            self.getControl(self.buttons[4]['id'
                            ]).controlRight(self.getControl(self.buttons[1]['id'
                    ]))

            self.getControl(self.buttons[1]['id'
                            ]).controlUp(self.getControl(self.buttons[4]['id'
                    ]))
            self.getControl(self.buttons[1]['id'
                            ]).controlLeft(self.getControl(self.buttons[4]['id'
                    ]))

            self.getControl(self.buttons[3]['id'
                            ]).controlRight(self.getControl(self.buttons[4]['id'
                    ]))

        except Exception, e:
            self.holo.dbg_log('holoWindows.wizard::set_wizard_button_2()', 'ERROR: (' + repr(e) + ')')

    def set_wizard_radiobutton_1(
        self,
        label,
        modul,
        action,
        selected=False,
        ):
        try:

            self.radiobuttons[1]['modul'] = modul
            self.radiobuttons[1]['action'] = action
            self.getControl(self.radiobuttons[1]['id']).setLabel(label)
            self.getControl(self.radiobuttons[1]['id']).setVisible(True)

            self.getControl(self.radiobuttons[1]['id'
                            ]).controlRight(self.getControl(self.buttons[1]['id'
                    ]))
            self.getControl(self.radiobuttons[1]['id'
                            ]).controlDown(self.getControl(self.buttons[1]['id'
                    ]))

            self.getControl(self.buttons[1]['id'
                            ]).controlUp(self.getControl(self.buttons[3]['id'
                    ]))
            self.getControl(self.buttons[1]['id'
                            ]).controlLeft(self.getControl(self.buttons[3]['id'
                    ]))

            self.getControl(self.radiobuttons[1]['id'
                            ]).setSelected(selected)
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_wizard_button_1()',
                            'ERROR: (' + repr(e) + ')')

    def set_wizard_radiobutton_2(
        self,
        label,
        modul,
        action,
        selected=False,
        ):
        try:

            self.radiobuttons[2]['modul'] = modul
            self.radiobuttons[2]['action'] = action
            self.getControl(self.radiobuttons[2]['id']).setLabel(label)
            self.getControl(self.radiobuttons[2]['id']).setVisible(True)

            self.getControl(self.radiobuttons[2]['id'
                            ]).controlLeft(self.getControl(self.radiobuttons[1]['id'
                    ]))
            self.getControl(self.radiobuttons[2]['id'
                            ]).controlDown(self.getControl(self.buttons[1]['id'
                    ]))
            self.getControl(self.radiobuttons[2]['id'
                            ]).controlRight(self.getControl(self.buttons[1]['id'
                    ]))

            self.getControl(self.buttons[1]['id'
                            ]).controlUp(self.getControl(self.radiobuttons[2]['id'
                    ]))
            self.getControl(self.buttons[1]['id'
                            ]).controlLeft(self.getControl(self.radiobuttons[2]['id'
                    ]))

            self.getControl(self.radiobuttons[1]['id'
                            ]).controlRight(self.getControl(self.radiobuttons[2]['id'
                    ]))

            self.getControl(self.radiobuttons[2]['id'
                            ]).setSelected(selected)
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_wizard_button_2()',
                            'ERROR: (' + repr(e) + ')')

    def onAction(self, action):
        pass

    def onClick(self, controlID):

        try:

            self.holo.dbg_log('wizard::onClick(' + str(controlID) + ')',
                            'enter_function', 0)

            for btn in self.buttons:
                if controlID == self.buttons[btn]['id'] \
                    and self.buttons[btn]['id'] > 1:
                    if hasattr(self.buttons[btn]['modul'],
                               self.buttons[btn]['action']):
                        getattr(self.buttons[btn]['modul'],
                                self.buttons[btn]['action'])()

            for btn in self.radiobuttons:
                if controlID == self.radiobuttons[btn]['id'] \
                    and self.radiobuttons[btn]['id'] > 1:
                    if hasattr(self.radiobuttons[btn]['modul'],
                               self.radiobuttons[btn]['action']):
                        getattr(self.radiobuttons[btn]['modul'],
                                self.radiobuttons[btn]['action'])()

            if controlID == self.guiNetList:
                selectedItem = \
                    self.getControl(controlID).getSelectedItem()

                if selectedItem.getProperty('action') != '':
                    if hasattr(self.holo.dictModules[self.last_wizard],
                               selectedItem.getProperty('action')):
                        getattr(self.holo.dictModules[self.last_wizard],
                                selectedItem.getProperty('action'
                                ))(selectedItem)
                        return

            if controlID == 1500:

                self.getControl(1390).setLabel('1')
                time.sleep(0.5)

                self.is_last_wizard = True

                self.getControl(1391).setLabel('')
                self.getControl(self.buttons[3]['id']).setVisible(False)
                self.getControl(self.buttons[4]['id']).setVisible(False)
                self.getControl(self.radiobuttons[1]['id'
                                ]).setVisible(False)
                self.getControl(self.radiobuttons[2]['id'
                                ]).setVisible(False)

                self.set_wizard_title('')
                self.set_wizard_text('')
                self.set_wizard_list_title('')
                self.set_wizard_button_title('')

                for strModule in sorted(self.holo.dictModules,
                        key=lambda x: \
                        self.holo.dictModules[x].menu.keys()):
                    if hasattr(self.holo.dictModules[strModule],
                               'do_wizard'):
                        if strModule == self.last_wizard:
                            if hasattr(self.holo.dictModules[strModule],
                                    'exit'):
                                self.holo.dictModules[strModule].exit()
                                if hasattr(self.holo.dictModules[strModule],
                                        'is_wizard'):
                                    del self.holo.dictModules[strModule].is_wizard

                        if self.holo.read_setting(strModule,
                                'wizard_completed') == None \
                            and strModule not in self.wizards:
                            self.last_wizard = strModule

                            if hasattr(self.holo.dictModules[strModule],
                                    'start_service'):
                                self.holo.dictModules[strModule].is_wizard = \
                                    True
                                self.holo.dictModules[strModule].start_service()

                            if hasattr(self.holo.dictModules[strModule],
                                    'do_init'):
                                self.holo.dictModules[strModule].do_init()

                            self.getControl(1390).setLabel('')
                            self.holo.dictModules[strModule].do_wizard()

                            self.wizards.append(strModule)
                            self.holo.write_setting(strModule,
                                    'wizard_completed', 'True')
                            self.is_last_wizard = False
                            break

                if self.is_last_wizard is True:
                    self.holo.write_setting('holovisi', 'wizard_completed', 'True')
                    self.close()
                    self.holo.start_service()

            self.holo.dbg_log('wizard::onClick(' + str(controlID) + ')',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::onClick()', 'ERROR: (' + repr(e) + ')')

    def onFocus(self, controlID):
        pass

    def showButton(self, number, name):
        try:

            button = self.getControl(self.buttons[number]['id'])
            button.setLabel(self.holo._(name))
            button.setVisible(True)
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::showButton('
                            + str(number) + ')', 'ERROR: (' + repr(e)
                            + ')')

    def addConfigItem(
        self,
        strName,
        dictProperties,
        strType,
        ):

        try:

            lstItem = xbmcgui.ListItem(label=strName)

            for strProp in dictProperties:
                lstItem.setProperty(strProp,
                                    str(dictProperties[strProp]))

            self.getControl(int(strType)).addItem(lstItem)

            return lstItem
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::addConfigItem('
                            + strName + ')', 'ERROR: (' + repr(e) + ')')

    def select_language(self):
        try:

            self.holo.dbg_log('holoWindows::select_language',
                            'enter_function', 0)

            languages = []
            currentLanguage = self.get_current_language()

            for filename in os.listdir(self.languages_dir):
                languages.append(filename)

            select_window = selectWindow('selectWindow.xml',
                    self.holo.__cwd__, 'Default', holoMain=self.holo)
            select_window.defaultValue = self.get_current_language()
            select_window.availValues = ','.join(languages)
            select_window.doModal()

            if currentLanguage != select_window.result:
                self.holo.language = select_window.result
                self.close()
                self.holo.set_language(select_window.result)

            del select_window

            self.holo.dbg_log('holoWindows::select_language', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('holoWindows.wizard::select_language()', 'ERROR: (' + repr(e) + ')')

    def get_current_language(self):
        try:

            if hasattr(self.holo, 'language'):
                return self.holo.language

            config_file = open(self.guisettings, 'r')
            config_text = config_file.read()
            config_file.close()

            xml_conf = minidom.parseString(config_text)

            for xml_entry in xml_conf.getElementsByTagName('locale'):
                for xml_modul in xml_entry.childNodes:
                    if xml_modul.nodeName == 'language':
                        if hasattr(xml_modul.firstChild, 'nodeValue'):
                            return xml_modul.firstChild.nodeValue

        except Exception, e:
            self.holo.dbg_log('holoWindows.wizard::get_current_language()', 'ERROR: (' + repr(e) + ')')

    def set_new_language(self, language):
        try:

            config_file = open(self.guisettings, 'r')
            config_text = config_file.read()
            config_file.close()

            xml_conf = minidom.parseString(config_text)

            for xml_entry in xml_conf.getElementsByTagName('locale'):
                for xml_modul in xml_entry.childNodes:
                    if xml_modul.nodeName == 'language':
                        xml_modul.firstChild.nodeValue = language

            config_file = open(self.guisettings, 'w')
            config_file.write(xml_conf.toprettyxml())
            config_file.close()

            os.system('killall xbmc.bin')
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_new_language('
                            + str(language) + ')', 'ERROR: (' + repr(e)
                            + ')')

    def get_keyboard_layout(self):
        try:

            current_layout = self.holo.dictModules['system'
                    ].config['keyboard']['settings']['KeyboardLayout1'
                    ]['value']

            return current_layout
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::get_keyboard_layout()',
                            'ERROR: (' + repr(e) + ')')

    def select_keyboard(self):
        try:

            self.holo.set_busy(1)
            select_window = selectWindow('selectWindow.xml',
                    self.holo.__cwd__, 'Default', holoMain=self.holo)
            select_window.defaultValue = self.holo.dictModules['system'
                    ].config['keyboard']['settings']['KeyboardLayout1'
                    ]['value']
            select_window.availValues = \
                ','.join(self.holo.dictModules['system'].config['keyboard'
                         ]['settings']['KeyboardLayout1']['values'])
            self.holo.set_busy(0)
            select_window.doModal()

            if select_window.defaultValue != select_window.result:
                self.holo.dictModules['system'].config['keyboard'
                        ]['settings']['KeyboardLayout1']['value'] = \
                    select_window.result
                self.holo.write_setting('system', 'KeyboardLayout1',
                        select_window.result)
                self.holo.dictModules['system'].set_keyboard_layout()
                self.set_wizard_button_2(self.holo._(32310)
                        + self.get_keyboard_layout(), self,
                        'select_keyboard')

            del select_window
        except Exception, e:

            self.holo.dbg_log('holoWindows.wizard::set_new_keyboard()',
                            'ERROR: (' + repr(e) + ')')

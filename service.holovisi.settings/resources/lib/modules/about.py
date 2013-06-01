# -*- coding: utf-8 -*-


class about:

    menu = {'99': {
        'name': 32196,
        'menuLoader': 'menu_loader',
        'listTyp': 'other',
        'InfoText': 705,
        }}

    def __init__(self, holoMain):
        try:

            holoMain.dbg_log('about::__init__', 'enter_function', 0)

            self.holo = holoMain
            self.controls = {}

            self.holo.dbg_log('about::__init__', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('about::__init__', 'ERROR: (' + repr(e)
                            + ')')

    def menu_loader(self, menuItem):
        try:

            self.holo.dbg_log('about::menu_loader', 'enter_function', 0)

            if len(self.controls) == 0:
                self.init_controls()

            self.holo.dbg_log('about::menu_loader', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('about::menu_loader', 'ERROR: (' + repr(e)
                            + ')', 4)

    def exit_addon(self):
        try:

            self.holo.dbg_log('about::exit_addon', 'enter_function', 0)

            self.holo.winHoloMain.close()

            self.holo.dbg_log('about::exit_addon', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('about::exit_addon', 'ERROR: (' + repr(e) + ')')

    def init_controls(self):
        try:

            self.holo.dbg_log('about::init_controls', 'enter_function', 0)

            distri = self.holo.load_file('/etc/distribution')
            arch = self.holo.load_file('/etc/arch')
            version = self.holo.load_file('/etc/version')
            build = self.holo.load_file('/etc/build')
            
            self.holo.winHoloMain.setProperty('arch', arch)
            self.holo.winHoloMain.setProperty('distri', distri)
            self.holo.winHoloMain.setProperty('version', version)
            self.holo.winHoloMain.setProperty('build', build)

            self.holo.dbg_log('about::init_controls', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('about::init_controls', 'ERROR: (' + repr(e) + ')')

    def exit(self):
        try:

            self.holo.dbg_log('about::exit', 'enter_function', 0)

            for control in self.controls:
                try:
                    self.holo.winHoloMain.removeControl(self.controls[control])
                except:
                    pass

            self.controls = {}

            self.holo.dbg_log('about::exit', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('about::exit', 'ERROR: (' + repr(e) + ')')

    def do_wizard(self):
        try:

            self.holo.dbg_log('about::do_wizard', 'enter_function', 0)

            self.holo.winHoloMain.set_wizard_title(self.holo._(32317))
            self.holo.winHoloMain.set_wizard_text(self.holo._(32318))

            self.holo.dbg_log('about::do_wizard', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('about::do_wizard', 'ERROR: (' + repr(e) + ')')

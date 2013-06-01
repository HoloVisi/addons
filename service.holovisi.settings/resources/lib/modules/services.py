# -*- coding: utf-8 -*-
import os
import xbmc
import ConfigParser
from StringIO import StringIO


class services:

    menu = {'4': {
        'name': 32001,
        'menuLoader': 'load_menu',
        'listTyp': 'list',
        'InfoText': 703,
        }}

    def __init__(self, holoMain):
        try:

            holoMain.dbg_log('services::__init__', 'enter_function', 0)

            self.struct = {
                'samba': {
                    'order': 1,
                    'name': 32200,
                    'not_supported': [],
                    'settings': {
                        'samba_autostart': {
                            'order': 1,
                            'name': 32204,
                            'value': '1',
                            'action': 'initialize_samba',
                            'typ': 'bool',
                            'InfoText': 738,
                            },
                        'samba_secure': {
                            'order': 2,
                            'name': 32202,
                            'value': '0',
                            'action': 'initialize_samba',
                            'typ': 'bool',
                            'parent': {'entry': 'samba_autostart',
                                    'value': ['1']},
                            'InfoText': 739,
                            },
                        'samba_username': {
                            'order': 3,
                            'name': 32106,
                            'value': 'holovisi',
                            'action': 'initialize_samba',
                            'typ': 'text',
                            'parent': {'entry': 'samba_secure',
                                    'value': ['1']},
                            'InfoText': 740,
                            },
                        'samba_password': {
                            'order': 4,
                            'name': 32107,
                            'value': 'holovisi',
                            'action': 'initialize_samba',
                            'typ': 'text',
                            'parent': {'entry': 'samba_secure',
                                    'value': ['1']},
                            'InfoText': 741,
                            },
                        },
                    },
                'ssh': {
                    'order': 2,
                    'name': 32201,
                    'not_supported': [],
                    'settings': {'ssh_autostart': {
                        'order': 1,
                        'name': 32205,
                        'value': '0',
                        'action': 'initialize_ssh',
                        'typ': 'bool',
                        'InfoText': 742,
                        }, 'ssh_unsecure': {
                        'order': 2,
                        'name': 32203,
                        'value': '0',
                        'action': 'initialize_ssh',
                        'typ': 'bool',
                        'parent': {'entry': 'ssh_autostart',
                                   'value': ['1']},
                        'InfoText': 743,
                        }},
                    },
                'avahi': {
                    'order': 3,
                    'name': 32207,
                    'not_supported': [],
                    'settings': {'avahi_autostart': {
                        'order': 1,
                        'name': 32206,
                        'value': '1',
                        'action': 'initialize_avahi',
                        'typ': 'bool',
                        'InfoText': 744,
                        }},
                    },
                'cron': {
                    'order': 3,
                    'name': 32319,
                    'not_supported': [],
                    'settings': {'cron_autostart': {
                        'order': 1,
                        'name': 32320,
                        'value': '0',
                        'action': 'initialize_cron',
                        'typ': 'bool',
                        'InfoText': 745,
                        }},
                    },
                'syslog': {
                    'order': 4,
                    'name': 32340,
                    'not_supported': [],
                    'settings': {'remote_syslog_autostart': {
                        'order': 1,
                        'name': 32341,
                        'value': '0',
                        'action': 'initialize_syslog',
                        'typ': 'bool',
                        'InfoText': 746,
                        }, 'remote_syslog_ip': {
                        'order': 2,
                        'name': 32342,
                        'value': '0',
                        'action': 'initialize_syslog',
                        'typ': 'ip',
                        'parent': {'entry': 'remote_syslog_autostart',
                                   'value': ['1']},
                        'InfoText': 747,
                        }},
                    },
                }

            self.kernel_cmd = '/proc/cmdline'
            
            self.samba_conf = '/var/run/smb.conf'
            self.samba_user_conf = '/storage/.config/samba.conf'
            self.samba_default_conf = '/etc/samba/smb.conf'
            self.samba_nmbd_pid = '/var/run/nmbd-smb.conf.pid'
            self.samba_smbd_pid = '/var/run/smbd-smb.conf.pid'
            self.samba_username_map = '/var/run/samba.map'
            self.samba_nmbd = '/usr/bin/nmbd'
            self.samba_smbd = '/usr/bin/smbd'

            self.ssh_dir = '/storage/.cache/ssh'
            self.ssh_rsa_key1 = '/storage/.cache/ssh/ssh_host_key'
            self.ssh_rsa_key2 = '/storage/.cache/ssh/ssh_host_rsa_key'
            self.ssh_dsa_key1 = '/storage/.cache/ssh/ssh_host_dsa_key'
            self.ssh_keygen = 'ssh-keygen'
            self.ssh_known_hosts_t = '/etc/ssh/known_hosts'
            self.ssh_known_hosts = os.environ['HOME'] \
                + '/.ssh/known_hosts'
            self.ssh_daemon = '/usr/sbin/sshd'
            self.ssh_pid = '/var/run/sshd.pid'
            self.ssh_conf_dir = '/storage/.config'
            self.ssh_conf_file = 'sshd.conf'
            self.sshd_init = '/etc/init.d/51_sshd'

            self.avahi_dir = '/var/run/avahi-daemon'
            self.avahi_daemon = '/usr/sbin/avahi-daemon'

            self.cron_dir = '/storage/.cache/cron/crontabs'
            self.cron_daemon = '/sbin/crond'

            self.syslog_daemon = '/sbin/syslogd'
            self.syslog_conf_file = '/storage/.cache/syslog/remote'
            self.syslog_pid = '/var/run/syslogd.pid'
            self.syslog_start = '/etc/init.d/08_syslogd'

            self.holo = holoMain

      # self.load_values()

            holoMain.dbg_log('services::__init__', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::__init__', 'ERROR: (%s)'
                            % repr(e))

    def start_service(self):
        try:

            self.load_values()

            self.holo.dbg_log('services::start_service', 'enter_function', 0)

            self.initialize_samba(service=1)

            # self.initialize_ssh(service=1)

            self.initialize_avahi(service=1)
            self.initialize_cron(service=1)

            self.holo.dbg_log('services::start_service', 'exit_function', 0)

        except Exception, e:
            self.holo.dbg_log('services::start_service', 'ERROR: (%s)' % repr(e))

    def do_init(self):
        try:

            self.holo.dbg_log('services::do_init', 'exit_function', 0)
            self.holo.dbg_log('services::do_init', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::do_init', 'ERROR: (%s)'
                            % repr(e))

    def load_menu(self, focusItem):

        try:

            self.holo.dbg_log('services::load_menu', 'enter_function', 0)

            for category in sorted(self.struct, key=lambda x: \
                                   self.struct[x]['order']):
                if 'not_supported' in self.struct[category]:
                    if self.arch \
                        in self.struct[category]['not_supported'] \
                        or not hasattr(self, category):
                        continue

                self.holo.winHoloMain.addConfigItem(self.holo._(self.struct[category]['name'
                        ]), {'typ': 'separator'},
                        focusItem.getProperty('listTyp'))

                for setting in sorted(self.struct[category]['settings'
                        ], key=lambda x: \
                        self.struct[category]['settings'][x]['order']):   

                    if 'not_supported' in self.struct[category]['settings'][setting]:

                        #skip setting
                        self.holo.dbg_log('services::load_menu', 'skip setting ' + setting, 0)
                        
                    else:
                      
                        dictProperties = {
                            'entry': setting,
                            'category': category,
                            'action': self.struct[category]['settings'
                                    ][setting]['action'],
                            'value': self.struct[category]['settings'
                                    ][setting]['value'],
                            'typ': self.struct[category]['settings'
                                    ][setting]['typ'],
                            }

                        if 'InfoText' in self.struct[category]['settings'
                                ][setting]:
                            dictProperties['InfoText'] = \
                                self.holo._(self.struct[category]['settings'
                                    ][setting]['InfoText'])

                        if 'values' in self.struct[category]['settings'
                                ][setting]:
                            if len(self.struct[category]['settings'
                                  ][setting]['values']) > 0:
                                dictProperties['values'] = \
                                    ','.join(self.struct[category]['settings'
                                        ][setting]['values'])

                        if not 'parent' in self.struct[category]['settings'
                                ][setting]:

                            self.holo.winHoloMain.addConfigItem(self.holo._(self.struct[category]['settings'
                                    ][setting]['name']), dictProperties,
                                    focusItem.getProperty('listTyp'))
                        else:

                            if self.struct[category]['settings'
                                    ][self.struct[category]['settings'
                                      ][setting]['parent']['entry']]['value'
                                    ] in self.struct[category]['settings'
                                    ][setting]['parent']['value']:

                                self.holo.winHoloMain.addConfigItem(self.holo._(self.struct[category]['settings'
                                        ][setting]['name']),
                                        dictProperties,
                                        focusItem.getProperty('listTyp'))

            self.holo.dbg_log('services::load_menu', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::load_menu', 'ERROR: (%s)'
                            % repr(e))

    def load_values(self):
        try:

            self.holo.dbg_log('services::load_values', 'enter_function',
                            0)

            self.arch = self.holo.load_file('/etc/arch')

            # SSH
            if os.path.isfile(self.ssh_daemon):
                self.ssh = True

                if os.path.exists(self.ssh_conf_dir + '/'
                                  + self.ssh_conf_file):
                    ssh_file = open(self.ssh_conf_dir + '/'
                                    + self.ssh_conf_file, 'r')
                    for line in ssh_file:
                        if 'SSHD_START' in line:
                            if line.split('=')[-1].lower().strip() \
                                == 'true':
                                self.struct['ssh']['settings'
                                        ]['ssh_autostart']['value'] = \
                                    '1'
                                self.holo.write_setting('services',
                                        'ssh_autostart', '1')
                            else:
                                self.struct['ssh']['settings'
                                        ]['ssh_autostart']['value'] = \
                                    '0'
                                self.holo.write_setting('services',
                                        'ssh_autostart', '0')

                        if 'SSHD_DISABLE_PW_AUTH' in line:
                            if line.split('=')[-1].lower().strip() \
                                == 'true':
                                self.struct['ssh']['settings'
                                        ]['ssh_unsecure']['value'] = '1'
                                self.holo.write_setting('services',
                                        'ssh_unsecure', '1')
                            else:
                                self.struct['ssh']['settings'
                                        ]['ssh_unsecure']['value'] = '0'
                                self.holo.write_setting('services',
                                        'ssh_unsecure', '0')

                    ssh_file.close()

                    cmd_file = open(self.kernel_cmd, 'r')
                    cmd_args = cmd_file.read()
                    if 'ssh' in cmd_args:
                        self.struct['ssh']['settings']['ssh_autostart'] \
                        ['not_supported'] = True

                    cmd_file.close()
                            
            if os.path.isfile(self.samba_nmbd) \
                and os.path.isfile(self.samba_smbd):
                self.samba = True
                for entry in self.struct['samba']['settings']:
                    value = self.holo.read_setting('services', entry)
                    if not value is None:
                        self.struct['samba']['settings'][entry]['value'
                                ] = value

            if os.path.isfile(self.avahi_daemon):
                self.avahi = True
                value = self.holo.read_setting('services',
                        'avahi_autostart')
                if not value is None:
                    self.struct['avahi']['settings']['avahi_autostart'
                            ]['value'] = value

            if os.path.isfile(self.cron_daemon):
                self.cron = True
                value = self.holo.read_setting('services',
                        'cron_autostart')
                if not value is None:
                    self.struct['cron']['settings']['cron_autostart'
                            ]['value'] = value

            if os.path.isfile(self.syslog_daemon):
                self.syslog = True
                value = self.holo.read_setting('services',
                        'remote_syslog_autostart')
                ip = self.holo.read_setting('services', 'remote_syslog_ip'
                        )
                if value != None and ip != None:
                    self.struct['syslog']['settings'
                            ]['remote_syslog_autostart']['value'] = \
                        value
                    self.struct['syslog']['settings']['remote_syslog_ip'
                            ]['value'] = ip

            self.holo.dbg_log('services::load_values', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::load_values', 'ERROR: (%s)'
                            % repr(e))

    def set_value(self, listItem=None):
        try:

            self.holo.dbg_log('services::set_value', 'enter_function', 0)

            self.struct[listItem.getProperty('category')]['settings'
                    ][listItem.getProperty('entry')]['value'] = \
                listItem.getProperty('value')

            self.holo.write_setting('services',
                                  listItem.getProperty('entry'),
                                  str(listItem.getProperty('value')))

            self.holo.dbg_log('services::set_value', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::set_value', 'ERROR: (%s)'
                            % repr(e), 4)

    def initialize_samba(self, **kwargs):
        try:

            self.holo.dbg_log('services::initialize_samba',
                            'enter_function', 0)

            self.holo.set_busy(1)

            if 'listItem' in kwargs:
                self.set_value(kwargs['listItem'])

            if self.struct['samba']['settings']['samba_autostart'
                    ]['value'] != '1':
                self.stop_samba()
                self.holo.dbg_log('services::initialize_samba',
                                'exit_function (samba disabled)', 0)
                self.holo.set_busy(0)
                return
            else:

                self.samba_active_conf = ConfigParser.ConfigParser()

                if os.path.isfile(self.samba_user_conf):
                    self.samba_active_conf.readfp(StringIO('\n'.join(line.strip()
                            for line in open(self.samba_user_conf))))
                else:
                    self.samba_active_conf.readfp(StringIO('\n'.join(line.strip()
                            for line in open(self.samba_default_conf))))

                if self.struct['samba']['settings']['samba_secure'
                        ]['value'] == '1' and self.struct['samba'
                        ]['settings']['samba_username']['value'] != '' \
                    and self.struct['samba']['settings'
                        ]['samba_password']['value'] != '':

                    os.system('echo -e "%(pw)s\n%(pw)s" | smbpasswd -s -a root >/dev/null 2>&1'
                               % {'pw': self.struct['samba']['settings'
                              ]['samba_password']['value']})

                    samba_map = open(self.samba_username_map, 'w')
                    samba_map.write('nobody = root\n')
                    samba_map.write('root = %s\n' % self.struct['samba'
                                    ]['settings']['samba_username'
                                    ]['value'])
                    samba_map.close()

                    for entry in self.samba_active_conf.sections():
                        if self.samba_active_conf.has_option(entry,
                                'public') and entry.lower() != 'global':
                            self.samba_active_conf.set(entry, 'public',
                                    'no')

                    self.samba_active_conf.set('global', 'security',
                            'user')

                    self.samba_active_conf.set('global', 'username map'
                            , self.samba_username_map)
                else:

                    for entry in self.samba_active_conf.sections():
                        if self.samba_active_conf.has_option(entry,
                                'public') and entry.lower() != 'global':
                            self.samba_active_conf.set(entry, 'public',
                                    'yes')

                    self.samba_active_conf.set('global', 'security',
                            'share')

                    if self.samba_active_conf.has_option('global',
                            'username map'):
                        self.samba_active_conf.remove_option('global',
                                'username map')

                with open(self.samba_conf, 'wb') as configfile:
                    self.samba_active_conf.write(configfile)

                self.stop_samba()

                os.system('%s --daemon --configfile=%s'
                          % (self.samba_nmbd, self.samba_conf))
                os.system('%s --daemon --configfile=%s'
                          % (self.samba_smbd, self.samba_conf))

                self.holo.dbg_log('services::initialize_samba',
                                'exit_function (samba enabled)', 0)

            self.holo.set_busy(0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('services::initialize_samba', 'ERROR: (%s)'
                            % repr(e), 4)

    def initialize_ssh(self, **kwargs):
        try:

            self.holo.dbg_log('services::initialize_ssh', 'enter_function'
                            , 0)

            self.holo.set_busy(1)

            if 'listItem' in kwargs:
                self.set_value(kwargs['listItem'])

            if self.struct['ssh']['settings']['ssh_autostart']['value'] \
                == '0':
                self.holo.dbg_log('services::initialize_ssh',
                                'exit_function (ssh disabled)', 0)

                if os.path.exists(self.ssh_conf_dir + '/'
                                  + self.ssh_conf_file):
                    os.remove(self.ssh_conf_dir + '/'
                              + self.ssh_conf_file)

                self.stop_ssh()
                self.holo.set_busy(0)
                return

            if not os.path.exists(self.ssh_conf_dir):
                os.makedirs(self.ssh_conf_dir)

            ssh_conf = open(self.ssh_conf_dir + '/'
                            + self.ssh_conf_file, 'w')
            ssh_conf.write('SSHD_START=true\n')
            if self.struct['ssh']['settings']['ssh_unsecure']['value'] \
                == '1':
                ssh_conf.write('SSHD_DISABLE_PW_AUTH=true\n')
            ssh_conf.close()

            self.stop_ssh()
            os.system('sh ' + self.sshd_init)

            self.holo.set_busy(0)

            self.holo.dbg_log('services::initialize_ssh',
                            'exit_function (ssh enabled)', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('services::initialize_ssh', 'ERROR: (%s)'
                            % repr(e), 4)

    def initialize_avahi(self, **kwargs):
        try:

            self.holo.dbg_log('services::initialize_avahi',
                            'enter_function', 0)

            self.holo.set_busy(1)

            if 'listItem' in kwargs:
                self.set_value(kwargs['listItem'])

            if self.struct['avahi']['settings']['avahi_autostart'
                    ]['value'] == '0':
                self.holo.dbg_log('services::initialize_avahi',
                                'exit_function (avahi disabled)', 0)
                self.stop_avahi()
                self.holo.set_busy(0)
                return

            if not os.path.exists(self.avahi_dir):
                os.mkdir(self.avahi_dir, 0755)

            self.stop_avahi()
            os.system(self.avahi_daemon + ' -D')

            self.holo.set_busy(0)

            self.holo.dbg_log('services::initialize_avahi',
                            'exit_function(avahi enabled)', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('services::initialize_avahi', 'ERROR: (%s)'
                            % repr(e), 4)

    def initialize_cron(self, **kwargs):
        try:

            self.holo.dbg_log('services::initialize_cron',
                            'enter_function', 0)

            self.holo.set_busy(1)

            if 'listItem' in kwargs:
                self.set_value(kwargs['listItem'])

            if self.struct['cron']['settings']['cron_autostart']['value'
                    ] == '0':
                self.holo.dbg_log('services::initialize_cron',
                                'exit_function (cron disabled)', 0)
                self.stop_cron()
                self.holo.set_busy(0)
                return

            if not os.path.exists(self.cron_dir):
                path = self.cron_dir.split('/')
                new_folder = ''

                for folder in path:
                    new_folder = new_folder + '/' + folder
                    if not os.path.exists(new_folder):
                        os.mkdir(new_folder, 0755)

            self.stop_cron()
            os.system(self.cron_daemon + ' -b')

            self.holo.set_busy(0)

            self.holo.dbg_log('services::initialize_cron',
                            'exit_function (cron enabled)', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('services::initialize_cron', 'ERROR: (%s)'
                            % repr(e), 4)

    def initialize_syslog(self, **kwargs):
        try:

            self.holo.dbg_log('services::initialize_syslog',
                            'enter_function', 0)

            self.holo.set_busy(1)

            if 'listItem' in kwargs:
                self.set_value(kwargs['listItem'])

            if self.struct['syslog']['settings'
                    ]['remote_syslog_autostart']['value'] == '1' \
                and self.struct['syslog']['settings']['remote_syslog_ip'
                    ]['value'] != '':

                if not os.path.exists(os.path.dirname(self.syslog_conf_file)):
                    os.makedirs(os.path.dirname(self.syslog_conf_file))

                config_file = open(self.syslog_conf_file, 'w')
                config_file.write('SYSLOG_REMOTE="true"\n')
                config_file.write('SYSLOG_SERVER="'
                                  + self.struct['syslog']['settings'
                                  ]['remote_syslog_ip']['value'] + '"\n'
                                  )
                config_file.close()
            else:

                if os.path.exists(self.syslog_conf_file):
                    os.remove(self.syslog_conf_file)

            self.stop_syslog()
            os.system('sh ' + self.syslog_start)

            self.holo.set_busy(0)

            self.holo.dbg_log('services::initialize_syslog',
                            'exit_function', 0)
        except Exception, e:

            self.holo.set_busy(0)
            self.holo.dbg_log('services::initialize_syslog', 'ERROR: (%s)'
                             % repr(e), 4)

    def stop_samba(self):
        try:

            self.holo.dbg_log('services::stop_samba', 'enter_function', 0)

            pid = self.holo.execute('pidof %s'
                                  % os.path.basename(self.samba_smbd)).split(' '
                    )
            for p in pid:
                self.holo.dbg_log('services::stop_samba PID', str(pid)
                                + ' --- ' + str(p), 0)
                os.system('kill ' + p.strip().replace('\n', ''))

            pid = self.holo.execute('pidof %s'
                                  % os.path.basename(self.samba_nmbd)).split(' '
                    )
            for p in pid:
                os.system('kill ' + p.strip().replace('\n', ''))

            if os.path.isfile(self.samba_nmbd_pid):
                os.remove(self.samba_nmbd_pid)

            if os.path.isfile(self.samba_smbd_pid):
                os.remove(self.samba_smbd_pid)

            self.holo.dbg_log('services::stop_samba', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::stop_samba', 'ERROR: (%s)'
                            % repr(e), 4)

    def stop_ssh(self):
        try:

            self.holo.dbg_log('services::stop_ssh', 'enter_function', 0)

            pid = self.holo.execute('pidof %s'
                                  % os.path.basename(self.ssh_daemon)).split(' '
                    )
            for p in pid:
                os.system('kill -9 ' + p.strip().replace('\n', ''))

            if os.path.isfile(self.ssh_pid):
                os.remove(self.ssh_pid)

            self.holo.dbg_log('services::stop_ssh', 'exit_function)', 0)
        except Exception, e:

            self.holo.dbg_log('services::stop_ssh', 'ERROR: (%s)'
                            % repr(e), 4)

    def stop_avahi(self):
        try:

            self.holo.dbg_log('services::stop_avahi', 'enter_function', 0)

            pid = self.holo.execute('pidof %s'
                                  % os.path.basename(self.avahi_daemon)).split(' '
                    )
            for p in pid:
                os.system('kill -9 ' + p.strip().replace('\n', ''))

            self.holo.dbg_log('services::stop_avahi', 'exit_function)', 0)
        except Exception, e:

            self.holo.dbg_log('services::stop_ssh', 'ERROR: (%s)'
                            % repr(e), 4)

    def stop_cron(self):
        try:

            self.holo.dbg_log('services::stop_cron', 'enter_function', 0)

            pid = self.holo.execute('pidof %s'
                                  % os.path.basename(self.cron_daemon)).split(' '
                    )
            for p in pid:
                os.system('kill -9 ' + p.strip().replace('\n', ''))

            self.holo.dbg_log('services::stop_cron', 'exit_function)', 0)
        except Exception, e:

            self.holo.dbg_log('services::stop_cron', 'ERROR: (%s)'
                            % repr(e), 4)

    def stop_syslog(self):
        try:

            self.holo.dbg_log('services::stop_syslog', 'enter_function',
                            0)

            pid = self.holo.execute('pidof %s'
                                  % os.path.basename(self.syslog_daemon)).split(' '
                    )
            for p in pid:
                os.system('kill -9 ' + p.strip().replace('\n', ''))

            if os.path.isfile(self.syslog_pid):
                os.remove(self.syslog_pid)

            self.holo.dbg_log('services::stop_syslog', 'exit_function)',
                            0)
        except Exception, e:

            self.holo.dbg_log('services::stop_syslog', 'ERROR: (%s)'
                            % repr(e), 4)

    def exit(self):
        try:

            self.holo.dbg_log('services::exit', 'enter_function', 0)
            self.holo.dbg_log('services::exit', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::exit', 'ERROR: (%s)' % repr(e),
                            4)

    def do_wizard(self):
        try:

            self.holo.dbg_log('services::do_wizard', 'enter_function', 0)

            self.holo.winHoloMain.set_wizard_title(self.holo._(32311))

            if hasattr(self, 'samba'):
                self.holo.winHoloMain.set_wizard_text(self.holo._(32313)
                        + '[CR][CR]' + self.holo._(32312))
            else:
                self.holo.winHoloMain.set_wizard_text(self.holo._(32312))

            self.holo.winHoloMain.set_wizard_button_title(self.holo._(32316))

            self.set_wizard_buttons()

            self.holo.dbg_log('services::do_wizard', 'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::do_wizard', 'ERROR: (%s)'
                            % repr(e))

    def set_wizard_buttons(self):
        try:

            self.holo.dbg_log('services::set_wizard_buttons',
                            'enter_function', 0)

            if self.struct['ssh']['settings']['ssh_autostart']['value'] \
                == '1':
                self.holo.winHoloMain.set_wizard_radiobutton_1(self.holo._(32201),
                        self, 'wizard_set_ssh', True)
            else:
                self.holo.winHoloMain.set_wizard_radiobutton_1(self.holo._(32201),
                        self, 'wizard_set_ssh')

            if hasattr(self, 'samba'):
                if self.struct['samba']['settings']['samba_autostart'
                        ]['value'] == '1':
                    self.holo.winHoloMain.set_wizard_radiobutton_2(self.holo._(32200),
                            self, 'wizard_set_samba', True)
                else:
                    self.holo.winHoloMain.set_wizard_radiobutton_2(self.holo._(32200),
                            self, 'wizard_set_samba')

            self.holo.dbg_log('services::set_wizard_buttons',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::set_wizard_buttons',
                            'ERROR: (%s)' % repr(e))

    def wizard_set_ssh(self):
        try:

            self.holo.dbg_log('services::wizard_set_ssh', 'enter_function'
                            , 0)

            if self.struct['ssh']['settings']['ssh_autostart']['value'] \
                == '1':
                self.struct['ssh']['settings']['ssh_autostart']['value'
                        ] = '0'
            else:
                self.struct['ssh']['settings']['ssh_autostart']['value'
                        ] = '1'

            self.holo.write_setting('services', 'ssh',
                                  str(self.struct['ssh']['settings'
                                  ]['ssh_autostart']['value']))
            self.struct['ssh']['settings']['ssh_autostart']['changed'
                    ] = True

            self.initialize_ssh()
            self.set_wizard_buttons()

            del self.struct['ssh']['settings']['ssh_autostart'
                    ]['changed']

            self.holo.dbg_log('services::wizard_set_ssh', 'exit_function'
                            , 0)
        except Exception, e:

            self.holo.dbg_log('services::wizard_set_ssh', 'ERROR: (%s)'
                            % repr(e))

    def wizard_set_samba(self):
        try:

            self.holo.dbg_log('services::wizard_set_samba',
                            'enter_function', 0)

            if self.struct['samba']['settings']['samba_autostart'
                    ]['value'] == '1':
                self.struct['samba']['settings']['samba_autostart'
                        ]['value'] = '0'
            else:
                self.struct['samba']['settings']['samba_autostart'
                        ]['value'] = '1'

            self.holo.write_setting('services', 'samba',
                                  str(self.struct['samba']['settings'
                                  ]['samba_autostart']['value']))
            self.struct['samba']['settings']['samba_autostart'
                    ]['changed'] = True

            self.initialize_samba()
            self.set_wizard_buttons()

            del self.struct['samba']['settings']['samba_autostart'
                    ]['changed']

            self.holo.dbg_log('services::wizard_set_samba',
                            'exit_function', 0)
        except Exception, e:

            self.holo.dbg_log('services::wizard_set_samba', 'ERROR: (%s)'
                            % repr(e))

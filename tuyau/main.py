import sys
import os.path
import ConfigParser
import argparse
from xdg import BaseDirectory
from gnupg import GPG
from . import application
from .document import Mail
from .application import Application

class Tuyau(object):
    def make_argument_parser(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers()

        new = subparsers.add_parser('new', help='add a new document')
        new.set_defaults(func=self.new)

        new_subparsers = new.add_subparsers()
        new_mail = new_subparsers.add_parser('mail',
                                             help='mail document (contents read on stdin)')
        new_mail.set_defaults(constructor=Mail)
        new_mail.set_defaults(needs_content=True)
        new_mail.add_argument('--filename',
                              help='filename of the message')
        new_mail.add_argument('--folder',
                              help='folder of the message')

        sync = subparsers.add_parser('sync', help='synchronize with other instances')
        sync.set_defaults(func=self.sync)

        return parser

    def new(self, app, cli):
        opts = vars(cli).copy()
        del opts['func']
        cls = opts.pop('constructor')
        if opts.pop('needs_content'):
            opts['content'] = sys.stdin.read()
        o = cls(**opts)
        print o, vars(o)
        #return app.save(o)

    def sync(self, app, cli):
        return app.sync()

    def get_config(self, cli):
        config = ConfigParser.SafeConfigParser()
        config.add_section('general')
        config.set('general', 'couch_url', 'http://localhost:5984/tuyau')
        config.set('general', 'instance_name', '')

        read_config = False
        filepath = 'tuyau.rc'
        for dir in BaseDirectory.load_config_paths('tuyau'):
            filename = os.path.join(dir, filepath)
            if not os.path.exists(filename): continue
            with file(filename) as f:
                read_config = True
                config.readfp(f)

        path = os.path.join(BaseDirectory.save_config_path('tuyau'), 'tuyau.rc')
        if not read_config:
            self.write_empty_config(config, path)

        if not config.get('general', 'instance_name'):
            print("Config missing! Edit {} and fill in couch_url\n"
                  "and instance_name".format(path))

        return read_config and config

    def write_empty_config(self, config, conffile):
        rootdir = BaseDirectory.save_config_path('tuyau')
        with file(conffile, 'wb') as fp:
            config.write(fp)

        g = GPG(gnupghome=os.path.join(rootdir, 'gnupg'))
        g.list_keys()

    def go(self):
        parser = self.make_argument_parser()
        opts = parser.parse_args()

        config = self.get_config(opts)
        if not config: return

        rootdir = BaseDirectory.save_config_path('tuyau')
        app = Application(config.get('general', 'instance_name'),
                          config.get('general', 'couch_url'),
                          gpg_keyring=os.path.join(rootdir, 'gnupg'))

        opts.func(app, opts)

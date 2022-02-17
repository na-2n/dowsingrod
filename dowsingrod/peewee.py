"""
Extracted from https://github.com/coleifer/flask-peewee

Licensed under the MIT license, see https://github.com/coleifer/flask-peewee/blob/master/LICENSE
"""

import sys
import peewee

from typing import Optional
from flask import Flask
from peewee import Model


class ImproperlyConfigured(Exception):
    pass


def load_class(s):
    path, klass = s.rsplit('.', 1)
    __import__(path)
    mod = sys.modules[path]
    return getattr(mod, klass)

class Database(object):
    def __init__(self, app: Optional[Flask] = None):
        self._app: Flask = app

        self._load_database()
        self._register_handlers()

        self.Model = self._get_model_class()

    def _load_database(self):
        self._database_config = dict(self._app.config['DATABASE'])
        try:
            self._database_name = self._database_config.pop('name')
            self._database_engine = self._database_config.pop('engine')
        except KeyError:
            raise ImproperlyConfigured('Please specify a "name" and "engine" for your database')

        try:
            self._database_class = load_class(self._database_engine)
            assert issubclass(self._database_class, peewee.Database)
        except ImportError:
            raise ImproperlyConfigured('Unable to import: "%s"' % self._database_engine)
        except AttributeError:
            raise ImproperlyConfigured('Database engine not found: "%s"' % self._database_engine)
        except AssertionError:
            raise ImproperlyConfigured('Database engine not a subclass of peewee.Database: "%s"' % self._database_engine)

        self._database: peewee.Database = self._database_class(self._database_name, **self._database_config)

    def _get_model_class(self):
        class BaseModel(Model):
            class Meta:
                database = self._database

        return BaseModel

    def _connect_db(self):
        if self._database.is_closed():
            self._database.connect()

    def _close_db(self, exc):
        if not self._database.is_closed():
            self._database.close()

    def _register_handlers(self):
        self._app.before_request(self._connect_db)
        self._app.teardown_request(self._close_db)


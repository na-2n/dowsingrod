import toml

from flask import Flask
from flask_peewee.db import Database
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config.from_file("config.toml", load=toml.load)

limiter = Limiter(app, key_func=get_remote_address, default_limits=['2/second'])
db = Database(app)
lm = LoginManager(app)
csrf = CSRFProtect(app)


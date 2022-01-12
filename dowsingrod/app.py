import toml

from flask import Flask
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from dowsingrod.dowsingrod import DowsingRod
from dowsingrod.peewee import Database


app = Flask(__name__)
app.config.from_file('../config.toml', load=toml.load)

limiter = Limiter(app, key_func=get_remote_address, default_limits=['2/second'])
db = Database(app)
lm = LoginManager(app)
csrf = CSRFProtect(app)
rod = DowsingRod(app)

from dowsingrod.blueprints import api, admin

app.register_blueprint(api.mod)
app.register_blueprint(admin.mod)



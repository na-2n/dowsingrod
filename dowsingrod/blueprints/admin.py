from flask import Blueprint


mod = Blueprint('admin', __name__, url_prefix='/admin')

@mod.route('/login', methods=['GET', 'POST'])
def login():
    pass


from flask import Blueprint, request


admin = Blueprint(__name__, 'admin_blueprint')

@admin.route('/login', method=['GET', 'POST'])
def login():


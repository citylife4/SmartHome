from flask import Blueprint

blueprint = Blueprint('auth', __name__)

from web_app.auth import routes

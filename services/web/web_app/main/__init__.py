from flask import Blueprint

blueprint = Blueprint('app', __name__)

from web_app.main import routes

# url_prefix='/homecontrol'

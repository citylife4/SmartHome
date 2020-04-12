from flask import Blueprint

blueprint = Blueprint('app', __name__)

from project.main import routes

# url_prefix='/homecontrol'

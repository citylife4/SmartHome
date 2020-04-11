from flask import Blueprint

blueprint = Blueprint('auth', __name__)

from project.auth import routes


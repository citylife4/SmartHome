import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
# from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_bcrypt import Bcrypt
# from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import config

# from elasticsearch import Elasticsearch
# from redis import Redis
# import rq

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bcrypt = Bcrypt()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
# mail = Mail()
bootstrap = Bootstrap()
# moment = Moment()
babel = Babel()


def create_homedash_app(config_class=config.Config):
    homedash = Flask(__name__)
    homedash.config.from_object(config_class)

    db.init_app(homedash)
    migrate.init_app(homedash, db)
    login.init_app(homedash)
    bcrypt.init_app(homedash)
    # mail.init_app(app)
    bootstrap.init_app(homedash)
    # moment.init_app(app)
    babel.init_app(homedash)
    # app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    # if app.config['ELASTICSEARCH_URL'] else None
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

    # from app.errors import blueprint as errors_blueprint
    # app.register_blueprint(errors_blueprint)

    from .auth import blueprint as auth_blueprint
    homedash.register_blueprint(auth_blueprint, url_prefix=homedash.config['NGINX_URL'])
    #homedash.register_blueprint(auth_blueprint)

    from .main import blueprint as main_blueprint
    homedash.register_blueprint(main_blueprint, url_prefix=homedash.config['NGINX_URL'])
    #homedash.register_blueprint(main_blueprint)

    # from app.api import blueprint as api_blueprint
    # app.register_blueprint(api_blueprint, url_prefix='/api')

    if not homedash.debug and not homedash.testing:
        if homedash.config['MAIL_SERVER']:
            auth = None
            if homedash.config['MAIL_USERNAME'] or homedash.config['MAIL_PASSWORD']:
                auth = (homedash.config['MAIL_USERNAME'],
                        homedash.config['MAIL_PASSWORD'])
            secure = None
            if homedash.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(homedash.config['MAIL_SERVER'], homedash.config['MAIL_PORT']),
                fromaddr='no-reply@' + homedash.config['MAIL_SERVER'],
                toaddrs=homedash.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            homedash.logger.addHandler(mail_handler)

        if homedash.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            homedash.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            homedash.logger.addHandler(file_handler)
        homedash.config['TEMPLATES_AUTO_RELOAD'] = True
        homedash.logger.setLevel(logging.INFO)
        homedash.logger.info('Jdvalverde website startup')

    return homedash


app = create_homedash_app()

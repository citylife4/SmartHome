import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI         = os.getenv("DATABASE_URL", 'sqlite:///' + os.path.join(basedir, 'database.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS  = False
    STATIC_FOLDER                   = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER                    = f"{os.getenv('APP_FOLDER')}/project/media"
    SECRET_KEY                      = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    LOG_TO_STDOUT                   = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER                     = os.environ.get('MAIL_SERVER')
    MAIL_PORT                       = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS                    = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME                   = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD                   = os.environ.get('MAIL_PASSWORD')
    NGINX_URL                       = os.environ.get('NGINX_URL') or ''

    INTERNAL_SERVER = os.environ.get('RELAY_ADDR', "127.0.0.1")
    INTERNAL_PORT = 54897
    PER_PAGE = 20

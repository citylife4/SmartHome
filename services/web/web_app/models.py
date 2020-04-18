from datetime import datetime, timedelta
from math import ceil
import os, base64, json

from web_app import login, db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id              = db.Column('id',               db.Integer, primary_key=True)
    username        = db.Column('username',         db.String(20), unique=True, index=True)
    password        = db.Column('password',         db.String(172))
    email           = db.Column('email',            db.String(50), unique=True, index=True)
    registered_on   = db.Column('registered_on',    db.DateTime)
    last_login_date = db.Column('last_login_date',  db.DateTime)
    logged_in_bol   = db.Column('logged_in_bol',    db.Boolean)
    admin           = db.Column('admin',            db.Boolean)
    token           = db.Column(db.String(32), index=True, unique=True)
    token_expiration= db.Column(db.DateTime)

    def __init__(self, username, email, admin):
        self.username = username
        self.email = email
        self.registered_on = datetime.utcnow()
        self.last_login_date = datetime.utcnow()
        self.logged_in_bol = False
        self.admin = admin

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'last_login_date': self.last_login_date,
            'admin': self.admin
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'admin']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    @property
    def is_authenticated(self):
        return True
        # return true if user is authenticated, provided credentials

    @property
    def is_active(self):
        return True
        # return true if user is activte and authenticated

    @property
    def is_annonymous(self):
        return False
        # return true if annon, actual user return false

    def is_admin(self):
        return self.admin
        # return true if annon, actual user return false

    def change_login_in_status(self, bool):
        self.logged_in_bol = bool
        if not self.logged_in_bol:
            self.last_login_date = datetime.utcnow()
        db.session.commit()
        return self.logged_in_bol

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def check_password(self, password):
        # return check_password_hash(self.password, password)
        return bcrypt.check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8", "ignore")
    # Todo : add possibility to admins to create and delete users on site

    def verify_reset_password_token(self):
        return User.query.get(self.id)

    def __repr__(self):
        return '<User %r>' % self.username

class HomeLocationServer(db.Model):
    __tablename__ = "home_location_server"
    id       = db.Column('id', db.Integer, primary_key=True)
    location = db.Column('username',db.String(20), unique=True, index=True)


class PalacouloDoorStatus(db.Model):
    __tablename__ = "palacoulo_garage_door"

    id = db.Column('id', db.Integer, primary_key=True)
    date = db.Column('date', db.DateTime, index=True)
    door_status = db.Column('door_status', db.INT)

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'date': self.date,
            'door_status': self.door_status,
        }
        return data

    def __init__(self, door_state):
        self.door_status = door_state
        self.date = datetime.utcnow()

    def get_door_status(self):
        return self.door_status

    def get_date_hour(self):
        return self.date.strftime("%x %X")

    def get_hour(self):
        return self.date.strftime("%X")

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3


class Data(object):
    def __init__(self):
        """
            Sets the default values for the project
        """
        self.door_status = True

    def change_door(self):
        self.door_status = not self.door_status

    def get_door_status(self):
        return self.door_status


class PortoDoorStatus(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    date = db.Column('date', db.DateTime, index=True)
    opened = db.Column('door_status', db.String(20))

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'date': self.date,
            'opened': self.opened,
        }
        return data

    def __init__(self, door_state):
        self.opened = door_state
        self.date = datetime.utcnow()

    def get_opened_status(self):
        return self.opened

    def get_date_hour(self):
        return self.date.strftime("%x %X")

    def get_hour(self):
        return self.date.strftime("%X")


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def count_all_door_status_tables():
    return PortoDoorStatus.query.count()


def count_door_status_in_date(dates):
    return PortoDoorStatus.query.filter(PortoDoorStatus.date.strftime('%x') == dates).count()


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (self.page - left_current - 1 < num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

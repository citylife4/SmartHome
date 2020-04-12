from flask.cli import FlaskGroup

from project import create_homedash_app, db
from project.models import User

app = create_homedash_app()

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    name = 'admin'
    password = 'admin'
    email = 'admin@admin.com'
    u = User(username=name, email=email, admin=1)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()


if __name__ == "__main__":
    cli()

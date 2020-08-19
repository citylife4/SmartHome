from flask.cli import FlaskGroup

from web_app import create_homedash_app, db
from web_app.models import User

app = create_homedash_app()

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.create_all()
    db.session.commit()
    print(db.engine.table_names())


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

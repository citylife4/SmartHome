from flask_wtf import FlaskForm
from wtforms import DateField
# from wtforms import Form, StringField, PasswordField, validators, SubmitField
from wtforms import SubmitField


class DateForm(FlaskForm):
    dt = DateField('Escolhe uma data Ex: 2018-06-15 ',
                   format='%Y-%m-%d',
                   id="datepicker",
                   render_kw={'autocomplete': 'off'})

    submit = SubmitField('Go')

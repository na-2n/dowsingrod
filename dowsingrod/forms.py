from flask_wtf import FlaskForm, RecaptchaField
from wtforms import PasswordField, StringField
from wtforms.validators import AnyOf, InputRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired])
    password = PasswordField('Password', validators=[InputRequired])


VALID_TYPES = ['other', 'nsfw', 'unrelated']

class ReportForm(FlaskForm):
    recaptcha = RecaptchaField(validators=[InputRequired])

    type = StringField('Type', validators=[InputRequired, AnyOf(VALID_TYPES, message='Invalid report type')])
    info = StringField('Reason', validators=[Length(max=2048, message='Additional info is too long')])


from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import AnyOf, InputRequired, Length

from dowsingrod.hcaptcha import HCaptchaField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


VALID_REASONS = ['other', 'nsfw', 'unrelated']

class ReportForm(FlaskForm):
    hcaptcha = HCaptchaField()

    reason = StringField('Reason', validators=[InputRequired(), AnyOf(VALID_REASONS, message='Invalid report reason')])
    info = StringField('Additional Info', validators=[Length(max=2048, message='Additional info is too long')])


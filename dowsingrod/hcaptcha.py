"""
Based on https://github.com/wtforms/flask-wtf/tree/main/src/flask_wtf/recaptcha

Licensed under the BSD-3-Clause License, see https://github.com/wtforms/flask-wtf/blob/main/LICENSE.rst
"""

try:
    import ujson as json
except:
    import json

from urllib import request as http

from flask import current_app
from flask import request
from werkzeug.urls import url_encode
from wtforms import ValidationError
from wtforms.fields import Field

HCAPTCHA_VERIFY_SERVER_DEFAULT = 'https://hcaptcha.com/siteverify'
HCAPTCHA_ERROR_CODES = {
    'missing-input-secret': 'The secret parameter is missing.',
    'invalid-input-secret': 'The secret parameter is invalid or malformed.',
    'missing-input-response': 'The response parameter is missing.',
    'invalid-input-response': 'The response parameter is invalid or malformed.',
}


__all__ = ['HCaptcha', 'HCaptchaField']


class HCaptcha:
    """Validates a HCaptcha."""

    def __init__(self, message=None):
        if message is None:
            message = HCAPTCHA_ERROR_CODES['missing-input-response']
        self.message = message

    def __call__(self, form, field):
        if current_app.testing:
            return True

        if request.json:
            response = request.json.get('h-captcha-response', '')
        else:
            response = request.form.get('h-captcha-response', '')

        remote_ip = request.remote_addr

        if not response:
            raise ValidationError(field.gettext(self.message))

        if not self._validate_recaptcha(response, remote_ip):
            field.recaptcha_error = 'incorrect-captcha-sol'
            raise ValidationError(field.gettext(self.message))

    def _validate_recaptcha(self, response, remote_addr):
        """Performs the actual validation."""
        cfg = current_app.config['HCAPTCHA']

        try:
            secret = cfg['secret']
        except KeyError:
            raise RuntimeError('HCAPTCHA.secret is not set in Flask config') from None

        verify_server = cfg.get('HCAPTCHA_VERIFY_SERVER', HCAPTCHA_VERIFY_SERVER_DEFAULT)

        data = url_encode(
            {'secret': secret, 'remoteip': remote_addr, 'response': response}
        )

        http_response = http.urlopen(verify_server, data.encode('utf-8'))

        if http_response.code != 200:
            return False

        json_resp = json.loads(http_response.read())

        if json_resp['success']:
            return True

        for error in json_resp.get('error-codes', []):
            if error in HCAPTCHA_ERROR_CODES:
                raise ValidationError(HCAPTCHA_ERROR_CODES[error])

        return False


class HCaptchaField(Field):
    hcaptcha_error = None

    def __init__(self, label="", validators=[], **kwargs):
        super().__init__(label, [HCaptcha(), *validators], **kwargs)


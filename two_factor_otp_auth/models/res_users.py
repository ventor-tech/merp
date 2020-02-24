# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from base64 import b32encode, b64encode
from os import remove, urandom
from tempfile import mkstemp
from logging import getLogger
from contextlib import suppress

from odoo import fields, models, _
from odoo.exceptions import AccessError
from odoo.http import request

from ..exceptions import MissingOtpError, InvalidOtpError

_logger = getLogger(__name__)

try:
    import pyotp
    import qrcode

except ImportError as error:
    _logger.debug(error)


class ResUsers(models.Model):
    _inherit = "res.users"

    enable_2fa = fields.Boolean(
        string="Two Factor Authentication",
        inverse="_inverse_enable_2fa",
    )
    secret_code_2fa = fields.Char(
        string="Two Factor Authentication Secret Code",
        copy=False,
    )
    qr_image_2fa = fields.Binary(
        string="Two Factor Authentication QR Code",
        copy=False,
    )

    def write(self, vals):
        """
        Overload core method to check access rights for changing 2FA.
        If `enable_2fa` in `vals` check access for action
        via `_can_change_2f_auth_settings`.
        """
        if "enable_2fa" in vals:
            self._can_change_2f_auth_settings(self.env.user)

        return super(ResUsers, self).write(vals)

    def _inverse_enable_2fa(self):
        """
        Inverse `enable_2fa` - call `action_discard_2f_auth_credentials` method
        if value of the field become `false`
        """
        for user in self:
            if not user.enable_2fa:
                user.action_discard_2f_auth_credentials()

    def action_discard_2f_auth_credentials(self):
        """
        Remove values from fields `qr_image_2fa`, `auth_secret_code_2fa`.
        This method calling when value of the field `enable_2fa` become `false`.
        Field `enable_2fa` can be changed only after checking rights for this action
        in method `write` and no need to check rights for
        `action_discard_2f_auth_credentials`.
        """
        values = {
            "qr_image_2fa": False,
            "secret_code_2fa": False,
        }
        self.write(values)

    def action_disable_2f_auth(self):
        """
        Set `enable_2fa` field value to `False`.
        """
        values = {
            "enable_2fa": False,
        }
        self.write(values)

    def action_enable_2f_auth(self):
        """
        Set `enable_2fa` field value to `False`.
        """
        values = {
            "enable_2fa": True,
        }
        self.write(values)

    def _check_credentials(self, password):
        """
        Overload core method to also check Two Factor Authentication credentials.
        Raises:
         * odoo.addons.two_factor_otp_auth.exceptions.MissingOtpError - no
            `otp_code` in request params. Should be caught by controller and
            render and open enter "one-time-password" page or QR code creation
        """
        self.ensure_one()
        super(ResUsers, self)._check_credentials(password)
        if self.enable_2fa:
            params = request.params
            secret_code = self.secret_code_2fa or params.get("secret_code_2fa")
            if params.get("otp_code") is None:
                request.session.otk_uid = self.id
                raise MissingOtpError()
            else:
                # can trigger `InvalidOtpError`
                self._check_otp_code(
                    params.pop("otp_code"),
                    secret_code,
                )

    def _generate_secrets(self):
        """
        Generate QR-Code based on random set of letters
        Returns:
         * tuple - generated secret_code and binary qr-code
        """
        self.ensure_one()
        key = b32encode(urandom(10))
        code = pyotp.totp.TOTP(key).provisioning_uri(self.login)
        img = qrcode.make(code)
        _, file_path = mkstemp()  # creating temporary file
        img.save(file_path)

        with open(file_path, "rb") as image_file:
            qr_image_code = b64encode(image_file.read())

        # removing temporary file
        with suppress(OSError):
            remove(file_path)

        return key, qr_image_code

    @staticmethod
    def _can_change_2f_auth_settings(user):
        """
        Checking that user can make mass actions with 2FA settings.
        Argument:
        * user - `res.users` object
        Raises:
         * odoo.exceptions.AccessError: only users with `Mass Change 2FA Configuration
          for Users` rights can do this action
        """
        if not user.has_group("two_factor_otp_auth.mass_change_2fa_for_users"):
            raise AccessError(_(
                "Only users with 'Mass Change 2FA Configuration "
                "for Users' rights can do this operation!"
            ))

    @staticmethod
    def _check_otp_code(otp, secret):
        """
        Validate incoming one time password `otp` witch secret via `pyotp`
        library methods.
        Args:
         * otp(str/integer) - one time password
         * secret(str) - origin secret of QR Code for one time password
           generator
        Raises:
         * odoo.addons.two_factor_otp_auth.exceptions.InvalidOtpError -
            one-time-password. Should be caught by controller and return user
            to enter "one-time-password" page
        Returns:
         * bool - True
        """
        totp = pyotp.TOTP(secret)
        str_otp = str(otp)
        verify = totp.verify(str_otp)
        if not verify:
            raise InvalidOtpError()
        return True

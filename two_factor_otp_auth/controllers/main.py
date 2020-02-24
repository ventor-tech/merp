# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import http, _
from odoo.addons.web.controllers.main import Home
from odoo.http import request

from ..exceptions import MissingOtpError, InvalidOtpError


class Login2fa(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        """
        Overload core method to start Second Factor validation step
        """
        try:
            response = super(Login2fa, self).web_login(redirect, **kw)
        except MissingOtpError:
            # user will get into this block if login process is not fully successful
            # For example, when first login was successful, but 2FA token is missing
            # So we can start second authentication step (OTP)
            response = self._redirect_to_2fa()
        except InvalidOtpError:
            message = _("Your security code is wrong")
            response = self._redirect_to_2fa(message)
        else:
            params = request.params
            if params.get("login_success"):
                user = request.env.user
                if user and user.enable_2fa and not user.qr_image_2fa:
                    # If credentials are Okay, but a user doesn't have
                    # QR code, that mean it's first success login with
                    # one-time-password. Now QR Code with it's Secret
                    # Code can be saved into the user.
                    values = {
                        "qr_image_2fa": params.get("qr_code_2fa"),
                        "secret_code_2fa": params.get("secret_code_2fa"),
                    }
                    user.sudo().write(values)

        return response

    @staticmethod
    def _redirect_to_2fa(message=None):
        """
        Method to get response object that depends on user and request params values
        argument:
         *message(str) - error message
        Returns:
         *response object
        """
        values = request.params.copy()
        if message:
            values.update({
                "error": message,
            })
        user_id = request.session.otk_uid
        user = request.env["res.users"].sudo().browse(user_id)

        if user.qr_image_2fa or values.get("qr_code_2fa") or values.get("error"):
            template = "two_factor_otp_auth.verify_code"

        else:
            template = "two_factor_otp_auth.scan_code"

            secret_code, qr_code = user._generate_secrets()
            values.update({
                "qr_code_2fa": qr_code,
                "secret_code_2fa": secret_code,
            })

        return request.render(template, values)

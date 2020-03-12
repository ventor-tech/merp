# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MerpConfig(models.Model):
    _name = 'merp.config'
    _rec_name = 'key'
    _description = 'MERP Configuration'

    key = fields.Char(required=True, index=True)
    value = fields.Text(required=True)

    _sql_constraints = [
        ('key_uniq', 'unique (key)', 'Key must be unique.')
    ]

    @api.model
    def get_param(self, key, default=False):
        params = self.search_read([('key', '=', key)], fields=['value'], limit=1)
        return params[0]['value'] if params else default

    @api.model
    def set_param(self, key, value):
        param = self.search([('key', '=', key)])

        vals = {'value': value}
        if param:
            if value is not False and value is not None:
                param.write(vals)
            else:
                param.unlink()
        else:
            if value is not False and value is not None:
                vals.update(key=key)
                self.create(vals)

        return False

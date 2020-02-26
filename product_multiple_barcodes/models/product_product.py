# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    barcode_ids = fields.One2many(
        'product.barcode.multi',
        'product_id',
        string='Additional Barcodes'
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('name', operator, name), ('default_code', operator, name),
                      '|', ('barcode', operator, name), ('barcode_ids', operator, name)]
        product_id = self._search(expression.AND([domain, args]),
                                  limit=limit, access_rights_uid=name_get_uid)
        return self.browse(product_id).name_get()

    @api.constrains('barcode')
    def _check_unique_barcode(self):
        products = self.env['product.product'].search([
            ('barcode_ids', '!=', False)
        ])
        additional_barcode_names = products.barcode_ids.mapped('name')

        if self.barcode in additional_barcode_names:
            raise UserError(
                _(f'Barcode {self.barcode} already exists')
            )

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
        string='Additional Barcodes',
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

    @api.constrains('barcode', 'barcode_ids', 'active')
    def _check_unique_barcode(self):
        products = self.env['product.product'].search([
            '|',
            ('barcode', '!=', False),
            ('barcode_ids', '!=', False),
        ])

        additional_barcode_names = set(products.mapped('barcode_ids.name'))
        barcode_names = set(products.mapped('barcode'))
        res = additional_barcode_names & barcode_names

        if res:
            raise UserError(
                _('"The following barcode(s) were found in other active products: {0} .'
                  '\n Note: That product barcodes should not repeat themselves both in'
                  ' "Barcode" field and "Additional Barcodes" field.').format(", ".join(res))
            )

# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import Counter


class ProductProduct(models.Model):
    _inherit = 'product.product'

    barcode_ids = fields.One2many(
        'product.barcode.multi',
        'product_id',
        string='Additional Barcodes',
    )

    # THIS IS OVERRIDE SQL CONSTRAINTS.
    _sql_constraints = [
        ('barcode_uniq', 'check(1=1)', 'No error')
    ]

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

        barcodes = products.mapped('barcode') + products.mapped('barcode_ids.name')

        duplicate_barcodes = Counter(barcodes)
        doubles_barcodes = {element: count for element, count in
                              duplicate_barcodes.items() if count > 1 and element}

        if doubles_barcodes:
            raise UserError(
                _('The following barcode(s) were found in other active products: {0}.'
                  '\nNote that product barcodes should not repeat themselves both in '
                  '"Barcode" field and "Additional Barcodes" field.').format(
                        ", ".join(doubles_barcodes.keys())
                  )
            )

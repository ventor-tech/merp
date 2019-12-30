# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_ids = fields.One2many(
        related='product_variant_ids.barcode_ids',
        readonly=False
    )

    @api.model
    def create(self, vals):
        if vals.get('barcode_ids'):
            ctx = self.env.context.copy()
            ctx['barcode'] = vals['barcode_ids']
            self.env.context = ctx
        return super(ProductTemplate, self).create(vals)

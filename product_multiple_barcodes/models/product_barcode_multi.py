# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductBarcodeMulti(models.Model):
    _name = 'product.barcode.multi'

    name = fields.Char('Barcode')
    product_id = fields.Many2one('product.product', string='Product')

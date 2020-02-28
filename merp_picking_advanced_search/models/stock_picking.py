# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    product_id_not_moved = fields.Many2many(
        'product.product', string='Product Not Moved',
        compute='_compute_products_not_moved', related=False, store=True)

    @api.depends('move_line_ids.qty_done')
    def _compute_products_not_moved(self):
        for picking in self:
            res = self.env['product.product']
            for operation in picking.move_line_ids:
                if operation.qty_done < operation.product_qty:
                    res += operation.product_id
            picking.product_id_not_moved = res

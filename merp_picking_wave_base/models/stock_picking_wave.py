# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class PickingWave(models.Model):
    _inherit = 'stock.picking.batch'

    related_pack_operations = fields.Many2many(
        'stock.move.line', relation='wave_pack_operations',
        string='Operations',
        compute='_compute_related_pack_operations', store=True)

    operations_to_pick = fields.Many2many(
        'stock.move.line', relation='wave_operations_to_pick',
        string='Operations to Pick',
        compute='_compute_operations_to_pick', store=False)

    strategy_order_r = fields.Char(
        string='Strategy Order',
        compute='_compute_operations_to_pick',
        store=False,
    )

    @api.depends(
        'picking_ids',
        'picking_ids.move_line_ids',
    )
    def _compute_related_pack_operations(self):
        for rec in self:
            res = self.env['stock.move.line']
            for picking in rec.picking_ids:
                for operation in picking.move_line_ids:
                    res += operation
            rec.related_pack_operations = res

    @api.depends(
        'picking_ids',
        'picking_ids.move_line_ids',
        'picking_ids.move_line_ids.location_id',
        'picking_ids.move_line_ids.qty_done',
    )
    def _compute_operations_to_pick(self):
        strategy = self.env.user.company_id.outgoing_routing_strategy
        strategy_order = self.env.user.company_id.outgoing_routing_order

        for rec in self:
            picking_ids = rec.picking_ids.ids
            all_operations = self.env['stock.move.line'].search([
                ('picking_id', 'in', picking_ids),
            ])
            rec.strategy_order_r = self.env['stock.picking'].get_strategy_string(strategy,
                                                                                 strategy_order)
            rec.operations_to_pick = self.env['stock.picking'].sort_operations(all_operations,
                                                                               strategy,
                                                                               strategy_order)

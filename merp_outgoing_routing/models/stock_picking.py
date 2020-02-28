# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operations_to_pick = fields.Many2many(
        'stock.move.line', relation='picking_operations_to_pick',
        string='Operations to Pick',
        compute='_compute_operations_to_pick', store=False)

    strategy_order_r = fields.Char(
        string='Strategy Order',
        compute='_compute_operations_to_pick',
        store=False,
    )

    @api.depends(
        'move_line_ids',
        'move_line_ids.location_id',
        'move_line_ids.qty_done',
    )
    def _compute_operations_to_pick(self):
        strategy = self.env.user.company_id.outgoing_routing_strategy
        strategy_order = self.env.user.company_id.outgoing_routing_order

        for rec in self:
            all_operations = self.env['stock.move.line'].search([
                ('picking_id', '=', rec.id),
            ])
            rec.strategy_order_r = rec.get_strategy_string(strategy, strategy_order)
            rec.operations_to_pick = rec.sort_operations(all_operations, strategy, strategy_order)

    def get_strategy_string(self, strategy, strategy_order):
        settings = self.env['res.company'].fields_get([
            'outgoing_routing_strategy',
            'outgoing_routing_order',
        ])
        strategies = settings['outgoing_routing_strategy']['selection']
        orders = settings['outgoing_routing_order']['selection']

        result = _('Strategy Order: ') + ', '.join([
            dict(strategies)[strategy].lower(),
            dict(orders)[strategy_order].lower()
        ])
        return result

    def sort_operations(self, all_operations, strategy, strategy_order):
        validated_operations = all_operations.filtered(lambda op: op._compute_operation_valid())

        if strategy == 'product':
            result = validated_operations.sorted(
                key=lambda op: op.product_id.name,
                reverse=int(strategy_order)
            )
            return result

        result = validated_operations.sorted(
            key=lambda op: getattr(op.location_id, strategy, 'None'),
            reverse=int(strategy_order)
        )
        return result

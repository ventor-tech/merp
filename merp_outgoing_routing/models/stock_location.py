# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = "stock.location"

    removal_prio = fields.Integer(
        string='Removal Strategy Priority',
        default=0,
    )

    strategy_sequence = fields.Integer(
        string='Sequence',
        help='Sequence based on warehouse location outgoing strategy/order',
        compute='_compute_outgoing_strategy_sequence',
        store=False,
    )

    def _compute_outgoing_strategy_sequence(self):

        strategy = self.env.user.company_id.outgoing_routing_strategy
        strategy_order = self.env.user.company_id.outgoing_routing_order

        if strategy not in self:
            return

        order = '%s %s' % (strategy, ['asc', 'desc'][int(strategy_order)])
        res = self.search([], order=order)
        for sequence, location in enumerate(res):
            location.strategy_sequence = sequence

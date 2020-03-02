# Copyright 2020 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    removal_prio = fields.Integer(
        related="location_id.removal_prio",
        store=True,
    )

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        # THIS IS A OVERRIDE STANDARD METHOD
        strategy_order = self.env.user.company_id.outgoing_routing_order

        if removal_strategy == 'location_priority':
            return 'removal_prio %s, id' % (['ASC', 'DESC'][int(strategy_order)])
        return super(StockQuant, self)._get_removal_strategy_order(removal_strategy)

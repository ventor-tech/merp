# Copyright 2020 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == 'location_priority':
            return 'removal_prio ASC, id'
        return super(StockQuant, self)._get_removal_strategy_order(removal_strategy)

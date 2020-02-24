# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def sort_printer_picking_list(self, move_line_ids):
        """ sort list of pack operations by configured field
        """
        strategy = self.env.user.company_id.outgoing_routing_strategy
        strategy_order = self.env.user.company_id.outgoing_routing_order

        return self.sort_operations(move_line_ids, strategy, strategy_order)

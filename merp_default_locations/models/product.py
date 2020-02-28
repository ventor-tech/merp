# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_update_quantity_on_hand(self):
        res = super(ProductTemplate, self).action_update_quantity_on_hand()
        default_location_id = \
            self.env.user.default_inventory_location \
            and self.env.user.default_inventory_location.id or False

        if not default_location_id:
            default_location_id = \
                self.env.user.company_id.stock_inventory_location \
                and self.env.user.company_id.stock_inventory_location.id or False
        if default_location_id:
            res['context'].update({'default_location_id': default_location_id})
        return res

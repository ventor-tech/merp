# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    default_inventory_location = fields.Many2one(
        comodel_name='stock.location',
        string='Default Inventory Location',
    )

    default_warehouse = fields.Many2one(
        comodel_name='stock.warehouse',
    )

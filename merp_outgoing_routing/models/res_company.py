# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    outgoing_routing_strategy = fields.Selection(
        [
            ('name', 'Sort by source locations in alphabetical order'),
            ('removal_prio', 'Sort by location removal strategy priority'),
            ('product', 'Sort by product name'),
        ],
        string='Routing Strategy', default='name')

    outgoing_routing_order = fields.Selection(
        [
            ('0', 'Ascending (A-Z)'),
            ('1', 'Descending (Z-A)'),
        ],
        string='Routing Order', default='0')

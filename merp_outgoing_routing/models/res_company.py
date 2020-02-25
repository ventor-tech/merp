# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    outgoing_routing_strategy = fields.Selection(
        [
            ('name', 'Sort by source locations in alphabetical order'),
            ('removal_prio', 'Sort by location removal strategy priority'),
        ],
        string='Routing Strategy', default='name')

    outgoing_routing_order = fields.Selection(
        [
            ('0', 'Ascending (A-Z)'),   ### NEEED SPEACK  INT TO STR
            ('1', 'Descending (Z-A)'),  ### NEEEDD SPEACK INT TO STR
        ],
        string='Routing Order', default=0)

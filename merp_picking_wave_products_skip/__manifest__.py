# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ventor Picking Wave Product Skip',
    "version": "13.0.1.0.0",
    'author': 'VentorTech',
    'website': 'https://ventor.tech/',
    'license': 'LGPL-3',
    'installable': True,
    'images': ['static/description/main_banner.png'],
    'summary': 'Allows smart skip of products in picking waves',
    'depends': [
        'merp_picking_products_skip',
        'merp_picking_wave_base',
    ],
    'data': [
        'views/stock_picking.xml',
    ],
}

# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ventor Picking Wave Core Module',
    "version": "13.0.1.0.0",
    'author': 'VentorTech',
    'website': 'https://ventor.tech/',
    'license': 'LGPL-3',
    'installable': True,
    'images': ['static/description/main_banner.png'],
    'summary': 'Allows configurable picking/picking wave',
    'depends': [
        'merp_picking_wave_base',
    ],
    'data': [
        'views/stock_picking.xml',
        'views/stock_picking_wave.xml'
    ],
    'post_init_hook': 'post_init'
}

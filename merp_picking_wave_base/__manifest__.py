# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ventor Picking Wave Base Module',
    "version": "13.0.1.0.0",
    'author': 'VentorTech',
    'website': 'https://ventor.tech/',
    'license': 'LGPL-3',
    'installable': True,
    'images': ['static/description/main_banner.png'],
    'summary': 'Allows configurable picking/picking wave',
    'depends': [
        'stock_picking_batch',
        'merp_base',
        'merp_custom_access_rights',
        'merp_picking_advanced_search',
        'merp_outgoing_routing'
    ],
    'data': [
        'views/stock_picking_wave.xml',
        'views/res_config.xml'
    ],
}

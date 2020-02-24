# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ventor Stock Picking Report (sorted)',
    "version": "13.0.1.0.0",
    'author': 'VentorTech',
    'website': 'https://ventor.tech/',
    'license': 'LGPL-3',
    'installable': True,
    'images': ['static/description/main_banner.png'],
    'summary': 'Sort pack operations in report',
    'depends': [
        'merp_outgoing_routing',
    ],
    'data': [
        'views/report_stockpicking.xml',
    ],
}

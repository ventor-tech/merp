# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from datetime import datetime


class TestPickingAdvancedSearch(TransactionCase):

    def setUp(self):
        super(TestPickingAdvancedSearch, self).setUp()
        self.location_1 = self.env['stock.location'].create({
            'name': 'test_location_1',
        })
        self.location_2 = self.env['stock.location'].create({
            'name': 'test_location_2',
        })
        company = self.env.user.company_id
        picking_type = self.env['stock.picking.type'].search([], limit=1)
        self.stock_picking_1 = self.env['stock.picking'].create({
            'name': 'test_stock_picking_1',
            'location_id': self.location_1.id,
            'location_dest_id': self.location_2.id,
            'move_type': 'one',
            'company_id': company.id,
            'picking_type_id': picking_type.id
        })
        self.stock_picking_2 =self.env['stock.picking'].create({
            'name': 'test_stock_picking_2',
            'location_id': self.location_2.id,
            'location_dest_id': self.location_1.id,
            'move_type': 'one',
            'company_id': company.id,
            'picking_type_id': picking_type.id
        })
        self.stock_picking_3 = self.env['stock.picking'].create({
            'name': 'test_stock_picking_3',
            'location_id': self.location_2.id,
            'location_dest_id': self.location_1.id,
            'move_type': 'one',
            'company_id': company.id,
            'picking_type_id': picking_type.id
        })
        product_uom = self.env['uom.uom'].search([], limit=1, order='id')
        products = self.env['product.template'].search([], limit=3)
        self.move_line_1 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking_1.id,
            'qty_done': 10.0,
            'location_id': self.location_1.id,
            'date': datetime.now(),
            'location_dest_id': self.location_2.id,
            'product_uom_qty': 20.0,
            'product_uom_id': product_uom.id,
            'product_id': products[0].id
        })
        self.move_line_2 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking_2.id,
            'qty_done': 300.0,
            'location_id': self.location_2.id,
            'date': datetime.now(),
            'location_dest_id': self.location_1.id,
            'product_uom_qty': 25.0,
            'product_uom_id': product_uom.id,
            'product_id': products[1].id
        })
        self.move_line_3 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking_3.id,
            'qty_done': 10.0,
            'location_id': self.location_2.id,
            'date': datetime.now(),
            'location_dest_id': self.location_1.id,
            'product_uom_qty': 15.0,
            'product_uom_id': product_uom.id,
            'product_id': products[2].id
        })
        self.move_line_4 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking_3.id,
            'qty_done': 180.0,
            'location_id': self.location_1.id,
            'date': datetime.now(),
            'location_dest_id': self.location_2.id,
            'product_uom_qty': 15.0,
            'product_uom_id': product_uom.id,
            'product_id': products[1].id
        })

    def test_check_product_not_moved(self):
        self.assertEqual(len(self.stock_picking_1.product_id_not_moved), 1)
        self.assertEqual(len(self.stock_picking_2.product_id_not_moved), 0)
        self.assertEqual(len(self.stock_picking_3.product_id_not_moved), 1)

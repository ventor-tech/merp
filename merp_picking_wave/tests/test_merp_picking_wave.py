# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from datetime import datetime


class TestMerpPickingWave(TransactionCase):

    def setUp(self):
        super(TestMerpPickingWave, self).setUp()
        self.location_1 = self.env['stock.location'].create({
            'name': 'test_location_1',
            'removal_prio': 2
        })
        self.location_2 = self.env['stock.location'].create({
            'name': 'test_location_2',
            'removal_prio': 3
        })
        company = self.env.user.company_id
        self.picking_type = self.env['stock.picking.type'].search([], limit=2)
        self.stock_move_confirmed = self.env['stock.move'].search([('state', '=', 'confirmed')], limit=1)
        self.stock_move_assigned = self.env['stock.move'].search([('state', '=', 'assigned')], limit=1)
        self.stock_move_draft = self.env['stock.move'].search([('state', '=', 'draft')], limit=2)
        self.stock_move_cancel = self.env['stock.move'].search([('state', '=', 'cancel')], limit=1)
        self.stock_move_done = self.env['stock.move'].search([('state', '=', 'done')], limit=1)
        self.procurement_group = self.env['procurement.group'].create({
            'name': 'procurement_group_1',
            'move_type': 'direct'
        })
        self.stock_picking_1 = self.env['stock.picking'].create({
            'name': 'test_stock_picking_1',
            'location_id': self.location_1.id,
            'location_dest_id': self.location_2.id,
            'move_type': 'direct',
            'company_id': company.id,
            'picking_type_id': self.picking_type[0].id
        })
        self.stock_picking_2 = self.env['stock.picking'].create({
            'name': 'test_stock_picking_2',
            'location_id': self.location_2.id,
            'location_dest_id': self.location_1.id,
            'move_type': 'direct',
            'company_id': company.id,
            'picking_type_id': self.picking_type[0].id
        })
        self.picking_batch = self.env['stock.picking.batch'].create({
            'name': 'test_stock_picking_batch',
            'picking_ids': [(4, self.stock_picking_1.id)]
        })
        product_uom = self.env['uom.uom'].search([], limit=1, order='id')
        products = self.env['product.template'].search([], limit=2)
        self.move_line_1 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking_1.id,
            'qty_done': 10.0,
            'location_id': self.location_1.id,
            'date': datetime.now(),
            'location_dest_id': self.location_2.id,
            'product_uom_qty': 0.0,
            'product_uom_id': product_uom.id,
            'product_id': products[0].id
        })
        self.move_line_2 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking_1.id,
            'qty_done': 15.0,
            'location_id': self.location_2.id,
            'date': datetime.now(),
            'location_dest_id': self.location_1.id,
            'product_uom_qty': 0.0,
            'product_uom_id': product_uom.id,
            'product_id': products[1].id
        })

    def test_wave_with_creation_of_backorders_variant_1(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '0',
            'outgoing_wave_remove_not_moved': True
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_cancel.id), (4, self.stock_move_done.id)]
        })
        self.picking_batch.done_outgoing()
        self.assertEqual(self.stock_picking_1.state, 'done')

    def test_wave_with_creation_of_backorders_variant_2(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '0',
            'outgoing_wave_remove_not_moved': True
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_draft[0].id), (4, self.stock_move_draft[1].id)]
        })
        self.picking_batch.done_outgoing()
        self.assertEqual(self.stock_picking_1.batch_id.id, False)

    def test_wave_with_creation_of_backorders_variant_3(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '0',
            'outgoing_wave_remove_not_moved': False
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_draft[0].id), (4, self.stock_move_draft[1].id)]
        })
        self.picking_batch.done_outgoing()
        self.assertEqual(self.stock_picking_1.state, 'done')

    def test_wave_without_creating_backorders(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '1'
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_draft[0].id), (4, self.stock_move_draft[1].id)]
        })
        self.picking_batch.done_outgoing()
        backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', self.stock_picking_1.id)])
        self.assertEqual(backorder_pick.state, 'cancel')

    def test_move_wave_to_on_hold_variant_1(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '2'
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_cancel.id)]
        })
        self.picking_batch.done_outgoing()
        self.assertEqual(self.picking_batch.state, 'done')
        self.assertEqual(self.stock_picking_1.state, 'cancel')

    def test_move_wave_to_on_hold_variant_2(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '2'
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_draft[0].id), (4, self.stock_move_draft[1].id)]
        })
        self.picking_batch.done_outgoing()
        self.assertEqual(self.picking_batch.state, 'on_hold')

    def test_move_wave_to_on_hold_variant_3(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '2'
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_confirmed.id), (4, self.stock_move_assigned.id)]
        })
        self.move_line_1.write({
            'product_uom_qty': 15.0
        })
        self.move_line_1.write({
            'product_uom_qty': 20.0
        })
        self.picking_batch.done_outgoing()
        self.assertEqual(self.picking_batch.state, 'on_hold')

    def test_move_wave_to_on_hold_variant_4(self):
        self.env.user.company_id.write({
            'outgoing_wave_behavior_on_confirm': '2'
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_confirmed.id), (4, self.stock_move_assigned.id)]
        })
        self.picking_batch.done_outgoing()
        self.assertEqual(self.picking_batch.state, 'done')

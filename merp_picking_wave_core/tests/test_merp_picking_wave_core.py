# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from odoo.exceptions import Warning


class TestMerpPickingWaveCore(TransactionCase):

    def setUp(self):
        super(TestMerpPickingWaveCore, self).setUp()

        self.location_1 = self.env['stock.location'].create({
            'name': 'test_location_1',
            'removal_prio': 2
        })
        self.location_2 = self.env['stock.location'].create({
            'name': 'test_location_2',
            'removal_prio': 3
        })
        company = self.env.user.company_id

        def _update_quants(moves, qty: float):

            location = self.env.ref('stock.stock_location_stock')
            products = [move.product_id for move in moves]
            for product in products:
                self.env['stock.quant']._update_available_quantity(product, location, qty)
            return moves

        self.picking_type = self.env['stock.picking.type'].search([], limit=2)
        self.stock_move_confirmed = self.env['stock.move'].search([('state', '=', 'confirmed')], limit=1)
        self.stock_move_assigned = self.env['stock.move'].search([('state', '=', 'assigned')], limit=1)
        self.stock_move_draft = self.env['stock.move'].search([('state', '=', 'draft')], limit=4)
        self.stock_move_draft = _update_quants(self.stock_move_draft, 100.0)
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

    def test_picking_wave_type(self):

        self.assertEqual(self.picking_batch.picking_wave_type.id, self.picking_type[0].id)

    def test_done(self):

        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_confirmed.id), (4, self.stock_move_assigned.id)]
        })
        self.assertEqual(self.picking_batch.done().get('context').get('sub_done_called'), True)

    def test_confirm_picking(self):

        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_draft[0].id), (4, self.stock_move_draft[1].id)]
        })
        self.picking_batch.confirm_picking()
        self.assertEqual(self.picking_batch.state, 'in_progress')
        self.assertEqual(self.stock_picking_1.state, 'assigned')

        # because stock.moves can be merged we need to check which moves are stayed
        moves = [move for move in self.stock_move_draft if move in self.stock_picking_1.mapped('move_lines')]

        for stock_move in moves:
            self.assertEqual(stock_move.state, 'assigned')

    def test_first_proc_picking(self):

        self.stock_move_draft.write({
            'group_id': self.procurement_group.id
        })
        self.stock_picking_1.write({
            'move_lines': [(4, self.stock_move_draft[0].id), (4, self.stock_move_draft[1].id)]
        })
        self.stock_picking_2.write({
            'move_lines': [(4, self.stock_move_draft[2].id), (4, self.stock_move_draft[3].id)]
        })
        self.assertEqual(self.stock_picking_2.first_proc_picking, self.stock_picking_1.first_proc_picking)

    def test_create_stock_picking(self):

        self.assertEqual(self.stock_picking_1.batch_id.picking_wave_type.id, self.picking_type[0].id)
        with self.assertRaises(Warning):
            self.env['stock.picking.batch'].create({
                'name': 'test_stock_picking_batch',
                'picking_ids': [(4, self.stock_picking_1.id)],
                'picking_wave_type': self.picking_type[1].id
            })

    def test_write_stock_picking(self):

        self.picking_batch.write({
            'picking_wave_type': False
        })
        self.stock_picking_1.write({
            'picking_type_id': self.picking_type[1].id
        })
        self.assertEqual(self.picking_batch.picking_wave_type.id, self.picking_type[1].id)
        with self.assertRaises(Warning):
            self.stock_picking_1.write({
                'picking_type_id': self.picking_type[0].id
            })

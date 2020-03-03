# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo.tests.common import TransactionCase


class TestMerpQuantsLocationRouting(TransactionCase):

    def setUp(self):
        super(TestMerpQuantsLocationRouting, self).setUp()
        self.res_users_model = self.env['res.users']
        self.stock_location_model = self.env['stock.location']
        self.stock_warehouse_model = self.env['stock.warehouse']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.product_model = self.env['product.product']
        self.quant_model = self.env['stock.quant']

        self.picking_internal = self.env.ref('stock.picking_type_internal')
        self.picking_out = self.env.ref('stock.picking_type_out')
        self.location_supplier = self.env.ref('stock.stock_location_suppliers')

        self.company = self.env.ref('base.main_company')

        self.wh1 = self.stock_warehouse_model.create({
            'name': 'WH2',
            'code': 'WH2',
        })

        # Removal strategies:
        self.fifo = self.env.ref('stock.removal_fifo')
        self.lifo = self.env.ref('stock.removal_lifo')
        self.removal_location_priority = self.env.ref(
            'merp_outgoing_routing.removal_location_priority'
        )

        # Create locations:
        self.stock = self.stock_location_model.create({
            'name': 'Default Base',
            'usage': 'internal',
        })

        self.location_A = self.stock_location_model.create({
                'name': 'location_A',
                'usage': 'internal',
                'location_id': self.stock.id,
                'removal_prio': 1,
        })

        self.location_B = self.stock_location_model.create({
                'name': 'Location_B',
                'usage': 'internal',
                'location_id': self.stock.id,
                'removal_prio': 0,
        })

        self.stock_2 = self.stock_location_model.create({
            'name': 'Another Location',
            'usage': 'internal',
        })

        # Create a product
        self.product_1 = self.product_model.create({
            'name': 'Product 1',
            'type': 'product',
        })

        # Create quants
        today = date.today()
        quant_1 = self.quant_model.create({
                'product_id': self.product_1.id,
                'location_id': self.location_A.id,
                'quantity': 10.0,
                'in_date': today,
        })

        quant_2 = self.quant_model.create({
                'product_id': self.product_1.id,
                'location_id': self.location_B.id,
                'quantity': 5.0,
                'in_date': today,
        })

        self.quants = quant_1 + quant_2

    def _create_picking(self, picking_type, location, location_dest, qty):
        move_line_values = {
            'name': 'Default Test Move',
            'product_id': self.product_1.id,
            'product_uom': self.product_1.uom_id.id,
            'product_uom_qty': qty,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'price_unit': 2,
        }

        picking = self.stock_picking_model.create({
            'picking_type_id': picking_type.id,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'move_lines': [(0, 0, move_line_values)],
        })

        return picking

    def test_stock_removal_location_by_removal_location_priority(self):
        """Tests removal priority with Location Priority strategy."""
        self.stock.removal_strategy_id = self.removal_location_priority

        # Quants must start unreserved
        for quant in self.quants:
            self.assertEqual(
                quant.reserved_quantity,
                0.0,
                'Quant must not have reserved qty right now.'
            )

            if quant.location_id == self.location_A:
                self.assertEqual(
                    quant.removal_prio,
                    1,
                    'Removal Priority Location must be 1'
                )
            if quant.location_id == self.location_B:
                self.assertEqual(
                    quant.removal_prio,
                    0,
                    'Removal Priority Location must be 0'
                )

        self.assertEqual(
            self.quants[0].in_date,
            self.quants[1].in_date,
            'Dates must be Equal'
        )

        picking_1 = self._create_picking(
            self.picking_internal,
            self.stock,
            self.stock_2,
            5,
        )

        picking_1.flush()
        picking_1.action_confirm()
        picking_1.action_assign()

        # Quants must be reserved in Location B (lower removal_priority value).
        for quant in self.quants:
            if quant.location_id == self.location_A:
                self.assertEqual(
                    quant.reserved_quantity,
                    0.0,
                    'This quant must not have reserved qty.'
                )
            if quant.location_id == self.location_B:
                self.assertEqual(
                    quant.reserved_quantity,
                    5.0,
                    'This quant must have 5 reserved qty.'
                )

# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo.tests import common
from odoo.tests.common import TransactionCase


@common.at_install(False)
@common.post_install(True)
class TestClearGroupsOnChange(TransactionCase):

    def setUp(self):
        super(TestClearGroupsOnChange, self).setUp()
        self.imd_model = self.env['ir.model.data']
        self.partner_model = self.env['res.partner']
        self.user_model = self.env['res.users']
        self.group_model = self.env['res.groups']
        self.category_model = self.env['ir.module.category']
        self.user = self.user_model.create({
            'login': 'testuser',
            'partner_id': self.partner_model.create({
                'name': "USER TEST (ROLES)",
            }).id,
            'groups_id': [(6, 0, [])],
        })
        self.implied_group1 = self.group_model.create({'name': 'Implied 1'})
        self.implied_group2 = self.group_model.create({'name': 'Implied 2'})
        self.implied_group3 = self.group_model.create({'name': 'Implied 3'})
        self.category = self.category_model.create({'name': 'Application'})
        self.app_group1 = self.group_model.create({
            'name': 'Application Role 1',
            'category_id': self.category.id,
            'implied_ids': [(6, 0, [self.implied_group1.id, self.implied_group2.id])],
        })
        self.app_group2 = self.group_model.create({
            'name': 'Application Role 2',
            'category_id': self.category.id,
            'implied_ids': [(6, 0, [self.app_group1.id, self.implied_group3.id])],
        })

    def test_group_change(self):
        key = 'sel_groups_%s_%s' % (self.app_group1.id, self.app_group2.id)
        self.user.write({
            key: self.app_group2.id
        })
        user_group_ids = sorted(set(
            [group.id for group in self.user.groups_id]))
        expected_group_ids = sorted(set([self.implied_group1.id,
                                         self.implied_group2.id,
                                         self.implied_group3.id,
                                         self.app_group1.id,
                                         self.app_group2.id]))
        self.assertEqual(user_group_ids, expected_group_ids)
        # Change application role
        self.user.write({
            key: self.app_group1.id
        })
        user_group_ids = sorted(set(
            [group.id for group in self.user.groups_id]))
        expected_group_ids = sorted(set([self.implied_group1.id,
                                         self.implied_group2.id,
                                         self.app_group1.id]))
        self.assertEqual(user_group_ids, expected_group_ids)

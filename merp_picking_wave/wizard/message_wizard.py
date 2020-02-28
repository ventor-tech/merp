# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields as oe_fields, api, _


class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = oe_fields.Text()

    @api.model
    def default_get(self, fields):
        res = super(MessageWizard, self).default_get(fields)
        res['message'] = self.env.context.get('message')
        return res

    def wizard_view(self):
        view = self.env.ref('merp_picking_wave.view_message_wizard')

        return {
            'name': _('Message'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            # 'res_id': self.ids[0],
            'context': self.env.context,
        }

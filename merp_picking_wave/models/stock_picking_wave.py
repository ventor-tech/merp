# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _


class PickingWave(models.Model):
    _inherit = 'stock.picking.batch'

    def done_outgoing(self):
        message_obj = self.env['message.wizard']
        behavior = self.env.user.company_id.outgoing_wave_behavior_on_confirm
        remove_not_moved = self.env.user.company_id.outgoing_wave_remove_not_moved
        if int(behavior) in (0, 1):
            # i.e. close pickings in wave with/without creating backorders
            for wave in self:
                for picking in wave.picking_ids:
                    if picking.state in ('cancel', 'done'):
                        continue
                    picking_not_moved = all([x.qty_done == 0.0 for x in picking.move_line_ids])
                    if remove_not_moved and (picking.state == 'draft' or picking_not_moved):
                        # In draft or with no pack operations edited yet,
                        # remove from wave
                        picking.batch_id = False
                        continue
                    if picking.state != 'assigned':
                        picking.action_assign()
                    if picking.state == 'assigned':
                        if picking_not_moved:
                            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                                for move_line in move.move_line_ids:
                                    move_line.qty_done = move_line.product_uom_qty
                    picking.action_done()
                    backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', picking.id)])
                    if backorder_pick:
                        backorder_pick.write({'batch_id': False})
                        if int(behavior) == 1:
                            # i.e. close pickings in wave without creating backorders
                            backorder_pick.action_cancel()
                            picking.message_post(body=_("Back order <em>%s</em> <b>cancelled</b>.") % (backorder_pick.name))
            return super(PickingWave, self).done()

        elif int(behavior) == 2:
            print("We are moving On Hold")
            # i.e. move wave to on hold if not all pickings are confirmed
            message = ''
            on_hold = False
            for wave in self:
                for picking in wave.picking_ids:
                    if picking.state in ('cancel', 'done'):
                        continue
                    elif picking.state != 'assigned':
                        on_hold = True
                        continue
                    else:
                        if picking.move_line_ids.filtered(lambda o: o.qty_done < o.product_qty):
                            on_hold = True
                        else:
                            picking.action_done()

                if on_hold:
                    wave.write({'state': 'on_hold'})
                    message = _('''
Not all products were found in wave pickings.
Wave is moved to "On Hold" for manual processing.
                    ''')
                else:
                    self.write({'state': 'done'})
            if message:
                return message_obj.with_context(message=message).wizard_view()
            return True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def search_pickings_to_pick(self, name, warehouse_id):
        warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        if warehouse.delivery_steps == 'ship_only':
            picking_type_id = warehouse.out_type_id.id
        else:
            picking_type_id = warehouse.pick_type_id.id
        return self.search_read(domain=[
            ('picking_type_id', '=', picking_type_id),
            ('state', 'in', ('assigned', 'partially_available')),
            '|',
            ('name', '=', name),
            ('origin', '=', name)])

# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _


class PickingWave(models.Model):
    _inherit = 'stock.picking.batch'

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Related Warehouse',
        required=False)

    view_location_id = fields.Many2one(
        'stock.location', string='Related Warehouse View',
        related='warehouse_id.view_location_id', readonly=True)

    location_id = fields.Many2one(
        'stock.location', string='Related Location',
        required=False)

    picking_wave_type = fields.Many2one(
        'stock.picking.type', string='Wave Type',
        readonly=True, required=False)

    state = fields.Selection(selection_add=[('on_hold', 'On Hold')])

    @api.onchange('picking_ids')
    def onchange_picking_ids(self):
        if self.picking_ids:
            self.picking_wave_type = self.picking_ids[0].picking_type_id.id

    def done(self):
        res = True
        if self.env.context.get('sub_done_called'):
            return super(PickingWave, self).done()
        ws_to_done = dict.fromkeys(['incoming', 'outgoing', 'internal'], self.env['stock.picking.batch'])
        for wave in self:
            if wave.picking_wave_type and \
               wave.picking_wave_type.warehouse_id.pick_type_id.id == wave.picking_wave_type.id and \
               wave.picking_wave_type.warehouse_id.delivery_steps != 'ship_only':
                ws_to_done['outgoing'] += wave
            elif wave.picking_wave_type:
                ws_to_done[wave.picking_wave_type.code] += wave

        for code in ws_to_done.keys():
            if ws_to_done[code]:
                res = getattr(ws_to_done[code].with_context(sub_done_called=True), 'done_%s' % code)()

        return res

    def confirm_picking(self):
        # This method overried to avoid Exception "Nothing to check the availability for."
        # from module stock model stock.picking method action_assign
        # in case of wave contains pickings in different states
        # e.g. Ready to Transfer and Transferred
        self.write({'state': 'in_progress'})
        for wave in self:
            wave.picking_ids.filtered(lambda p: p.state == 'draft').action_confirm()
            for pick in wave.picking_ids:
                move_ids = pick.move_lines.filtered(lambda x: x.state not in ('draft', 'cancel', 'done'))
                if move_ids:
                    move_ids._action_assign()
        return True

    def done_incoming(self):
        # override this method in subclasses
        return super(PickingWave, self).done()

    def done_outgoing(self):
        # override this method in subclasses
        return super(PickingWave, self).done()

    def done_internal(self):
        # override this method in subclasses
        return super(PickingWave, self).done()


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    picking_ids = fields.One2many('stock.picking', 'group_id', 'Pickings')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    first_proc_picking = fields.Many2one(
        comodel_name='stock.picking',
        string='First picking from the same procurement group',
        readonly=True,
        store=True,
        compute='_compute_first_proc_picking',
    )

    wave_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Wave Location',
        readonly=True,
        store=True,
        related='first_proc_picking.batch_id.location_id',
    )

    @api.depends('group_id', 'group_id.picking_ids')
    def _compute_first_proc_picking(self):
        if self.env.context.get('module', '') == 'merp_picking_wave_core':
            # Do not recompute on installing module as it's done in pre_init hook
            wave_count = self.env['stock.picking.batch'].search_count([('location_id', '!=', False)])
            if not wave_count:
                return
        for picking in self:
            if not picking.group_id:
                picking.first_proc_picking = picking.id
                continue
            res = self.search([('group_id', '=', picking.group_id.id)], order='id asc', limit=1)
            if res:
                picking.first_proc_picking = res[0]

    @api.model
    def create(self, vals):
        picking = super(StockPicking, self).create(vals)
        if not picking.batch_id:
            return picking
        if not picking.batch_id.picking_wave_type:
            picking.batch_id.write({'picking_wave_type': picking.picking_type_id.id})
        elif picking.batch_id.picking_wave_type.id != picking.picking_type_id.id:
            raise exceptions.Warning(
                _('Picking cannot be added. All pickings in the current picking '
                    'wave should be from zone %s') % picking.batch_id.picking_wave_type.name
            )
        return picking

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        for picking in self:
            if not picking.batch_id:
                continue
            if not picking.batch_id.picking_wave_type:
                picking.batch_id.write({'picking_wave_type': picking.picking_type_id.id})
            elif picking.batch_id.picking_wave_type.id != picking.picking_type_id.id:
                raise exceptions.Warning(
                    _('Picking cannot be added. All pickings in the current picking '
                        'wave should be from zone %s') % picking.batch_id.picking_wave_type.name)
        return res

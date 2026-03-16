from odoo import fields, models, api, _


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    allow_creating_new_packages = fields.Boolean(
        string="Allow creating new packages",
        help="User can create new packages by scanning a new barcode or create it manually"
    )

    apply_default_lots = fields.Boolean(
        string="Apply default lots and serials",
        help="If it's on, you don't need to scan lot number to confirm it. "
             "On receipts the app will create default Odoo lots and apply them to the product. "
             "On delivery zone you don't need to confirm lots and "
             "they will be taken Odoo by default"
    )

    apply_quantity_automatically = fields.Boolean(
        string="Apply quantity automatically",
        help="Automatically validate the line after scanning a destination location. "
             "Warning: you have to insert QTY first before destination location"
    )

    autocomplete_the_item_quantity_field = fields.Boolean(
        string="Autocomplete item quantity",
        help="Automatically insert expected quantity. No need to enter the quantity "
             "of goods using the keyboard or using scanning"
    )

    behavior_on_backorder_creation = fields.Selection(
        [
            ("always_create_backorder", "Always Create Backorder"),
            ("never_create_backorder", "Never Create Backorder"),
            ("ask_me_every_time", "Ask Me Every Time"),
        ],
        string="Behavior On Backorder Creation",
        default="ask_me_every_time",
        required=True,
        help="Choose how to process backorders. You can always create backorders, "
             "always ignore backorders or choose it all the time (default)"
    )

    behavior_on_split_operation = fields.Selection(
        [
            ("always_split_line", "Always Split the Line"),
            ("always_move_less_items", "Always Move Less Items"),
            ("ask_me_every_time", "Ask Me Every Time"),
        ],
        string="Behavior On Split Operation",
        compute="_compute_behavior_on_split_operation",
        readonly=False,
        store=True,
        help="Choose how to process less product qty than initial. You can always split "
             "the line, always move less items or choose it all the time(default)"
    )

    change_destination_location = fields.Boolean(
        string="Change destination location",
        help="If this setting is active a user can change destination location "
             "while receiving to be placed at any available location",
    )

    change_lots = fields.Boolean(
        string="Change Lots and S/N",
        default=True,
        help="User can change Lots and Serial Numbers that Odoo reserves"
    )

    change_source_location = fields.Boolean(
        string="Change source location",
        help="User can change default source location to pick item from another location. "
             "Works only if 'Confirm source location' setting is active",
    )

    check_shipping_information = fields.Boolean(
        string="Check shipping information",
        help="If the setting is active the user can edit shipping information "
             "before validate OUT transfer",
    )

    confirm_destination_location = fields.Boolean(
        string="Confirm destination location",
        help="The dot next to the field gets yellow color means user has to confirm it. "
             "User has to scan a barcode of destination location"
    )

    confirm_product = fields.Boolean(
        string="Confirm product",
        help="The dot next to the field gets yellow color means user has to confirm it. "
             "User has to scan a barcode of product."
    )

    confirm_source_location = fields.Boolean(
        string="Confirm source location",
        help="The dot next to the field gets yellow color means user has to confirm it. "
             "User has to scan a barcode of source location"
    )

    confirm_source_package = fields.Boolean(
        string="Confirm source package",
        help="User has to scan a barcode of source package. "
             "The dot next to the field gets yellow color means user has to confirm it"
    )

    hide_qty_to_receive = fields.Boolean(
        string="Hide QTYs to receive",
        help="Setting’s description: User will not see how many QTYs they need to receive."
    )

    is_consignment_enabled = fields.Boolean(
        compute="_compute_is_consignment_enabled"
    )

    is_package_tracking_enabled = fields.Boolean(
        compute="_compute_is_package_tracking_enabled"
    )

    is_stock_production_lot_enabled = fields.Boolean(
        compute="_compute_is_stock_production_lot_enabled"
    )

    is_quality_control_module_installed = fields.Boolean(
        compute="_compute_is_quality_control_module_installed"
    )

    manage_packages = fields.Boolean(
        string="Show packages fields",
        default=lambda self: self.env.ref("stock.group_tracking_lot")
        in self.env.ref("base.group_user").implied_ids,
        help="Scan source (destination) packages right after scanning source (destination) "
             "location. Use it if you move from one package to another or pick items from "
             "packages or pallets. Works only if package management settings is active on Odoo "
             "side.\n\n If you want to use Show packages fields, you must turn on setting "
             "'Packages' in inventory settings",
    )

    manage_product_owner = fields.Boolean(
        string="Show Product Owner field",
        default=lambda self: self.env.ref("stock.group_tracking_owner")
        in self.env.ref("base.group_user").implied_ids,
        help="Allow scan product owner. You can specify product owner while moving items. "
             "Working only with 'Consignment' setting on Odoo side"
    )

    move_reserved_quantities = fields.Boolean(
        string="Move reserved quantities",
        help="Allows moving items reserved by other operations. "
             "'Move reserved quantities' is available only if 'Change source location' is enabled.",
    )

    open_details_screen_first = fields.Boolean(
        string="Open details screen first",
        default=False,
        help="Clicking on transfer card will bring details screen "
             "instead of opening a whole stock picking"
    )

    quality_check_per_product_line = fields.Boolean(
        string="Quality check per product line",
        help="If the setting is active the Quality check wizard will be shown automatically while "
             "processing each product line. Disable if you want to do the Quality check manually "
             "after all product lines are confirmed"
    )

    scan_destination_location_once = fields.Boolean(
        string="Scan destination location once",
        help="Scan the destination location only once with the last item. "
             "The destination location will be applied to all lines."
    )

    scan_destination_package = fields.Boolean(
        string="Confirm destination package",
        help="User has to scan a barcode of destination package. The dot next to the field "
             "gets yellow color means user has to confirm it"
    )

    scan_source_location_once = fields.Boolean(
        string="Scan source location once",
        help="Scan source location once for all lines in one location"
    )

    show_next_product = fields.Boolean(
        string="Show next product",
        help="Product field will show the next product to be picked. "
             "Use the setting during picking and delivery. "
             "It is recommended to disable the setting for the reception area",
    )

    show_only_lots_from_source_location = fields.Boolean(
        string="Show only lots from source location",
        default=False,
        help="If it is active you can see only Lots and SN from the source location",
    )

    show_print_attachment_button = fields.Boolean(
        string="Show Print attachments button",
        default=True,
        help="Showing the Print attachments button in the toolbar instead of "
             "keeping it in the hidden menu"
    )

    show_put_in_pack_button = fields.Boolean(
        string="Show Put in pack button",
        default=lambda self: self.env.ref("stock.group_tracking_lot")
        in self.env.ref("base.group_user").implied_ids,
        help="Showing the Put in pack button in the toolbar instead of "
             "keeping it in the hidden menu"
    )

    show_product_information = fields.Boolean(
        string="Show description from product",
        default=True,
        help="Show the description for the operation from Product->Inventory",
    )

    transfer_more_items = fields.Boolean(
        string="Move more than planned",
        help="Allows moving more items than expected (for example kg of meat, etc)"
    )

    @api.depends('code')
    def _compute_behavior_on_split_operation(self):
        for operation_type in self:
            if operation_type.code == 'incoming':
                operation_type.behavior_on_split_operation = 'always_split_line'
            else:
                operation_type.behavior_on_split_operation = 'ask_me_every_time'

    def _compute_is_consignment_enabled(self):
        internal_user_groups = self.env.ref('base.group_user').implied_ids
        group_tracking_owner = self.env.ref("stock.group_tracking_owner")
        for item in self:
            item.is_consignment_enabled = group_tracking_owner in internal_user_groups

    def _compute_is_package_tracking_enabled(self):
        internal_user_groups = self.env.ref('base.group_user').implied_ids
        group_tracking_lot = self.env.ref("stock.group_tracking_lot")
        for item in self:
            item.is_package_tracking_enabled = group_tracking_lot in internal_user_groups

    def _compute_is_stock_production_lot_enabled(self):
        internal_user_groups = self.env.ref('base.group_user').implied_ids
        group_production_lot = self.env.ref("stock.group_production_lot")
        for item in self:
            item.is_stock_production_lot_enabled = group_production_lot in internal_user_groups

    def _compute_is_quality_control_module_installed(self):
        is_qc_installed = self.is_module_installed('quality_control')
        for item in self:
            item.is_quality_control_module_installed = is_qc_installed

    @api.model
    def create(self, vals):
        if 'code' in vals:
            vals['show_next_product'] = vals['code'] != "incoming"
            vals['change_destination_location'] = True

        return super(StockPickingType, self).create(vals)

    @api.onchange('confirm_source_location')
    def _onchange_confirm_source_location(self):
        if not self.confirm_source_location:
            self.change_source_location = False
            self.scan_source_location_once = False

    @api.onchange('confirm_destination_location')
    def _onchange_confirm_destination_location(self):
        if not self.confirm_destination_location:
            self.apply_quantity_automatically = False

    @api.onchange('change_source_location')
    def _onchange_change_source_location(self):
        if self.change_source_location and not self.confirm_source_location:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("'Change source location' is available only "
                                 "if 'Confirm source location' is enabled")
                }
            }

    @api.onchange('apply_quantity_automatically')
    def _onchange_apply_quantity_automatically(self):
        if self.apply_quantity_automatically and not self.confirm_destination_location:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("'Apply quantity automatically' is available only "
                                 "if 'Confirm destination location' is enabled")
                }
            }

    def write(self, vals):
        res = super(StockPickingType, self).write(vals)

        if 'change_source_location' in vals or 'confirm_source_location' in vals:
            for stock_picking_type in self:
                if stock_picking_type.change_source_location:
                    if not stock_picking_type.confirm_source_location:
                        stock_picking_type.change_source_location = False
                if not stock_picking_type.change_source_location:
                    stock_picking_type.move_reserved_quantities = False
                if not stock_picking_type.confirm_source_location:
                    stock_picking_type.scan_source_location_once = False

        if 'apply_quantity_automatically' in vals or 'confirm_destination_location' in vals:
            for stock_picking_type in self:
                if stock_picking_type.apply_quantity_automatically:
                    if not stock_picking_type.confirm_destination_location:
                        stock_picking_type.apply_quantity_automatically = False

        if 'manage_packages' in vals:
            for stock_picking_type in self:
                if not stock_picking_type.manage_packages:
                    if stock_picking_type.scan_destination_package:
                        stock_picking_type.scan_destination_package = False
                    if stock_picking_type.confirm_source_package:
                        stock_picking_type.confirm_source_package = False
                    if stock_picking_type.allow_creating_new_packages:
                        stock_picking_type.allow_creating_new_packages = False
        return res

    def get_warehouse_operation_settings(self):
        return {
            "id": self.id,
            "name": self.name,
            "wh_code": self.warehouse_id.code,
            "wh_name": self.warehouse_id.name,
            "settings": {
                "allow_creating_new_packages": self.allow_creating_new_packages,
                "confirm_source_location": self.confirm_source_location,
                "change_source_location": self.change_source_location,
                "scan_source_location_once": self.scan_source_location_once,
                "show_next_product": self.show_next_product,
                "confirm_product": self.confirm_product,
                "apply_default_lots": self.apply_default_lots,
                "change_lots": self.change_lots,
                "show_only_lots_from_source_location": self.show_only_lots_from_source_location,
                "transfer_more_items": self.transfer_more_items,
                "confirm_destination_location": self.confirm_destination_location,
                "apply_quantity_automatically": self.apply_quantity_automatically,
                "change_destination_location": self.change_destination_location,
                "scan_destination_location_once": self.scan_destination_location_once,
                "autocomplete_the_item_quantity_field": self.autocomplete_the_item_quantity_field,
                "show_print_attachment_button": self.show_print_attachment_button,
                "show_put_in_pack_button": self.show_put_in_pack_button,
                "manage_packages": self.manage_packages,
                "manage_product_owner": self.manage_product_owner,
                "move_reserved_quantities": self.move_reserved_quantities,
                "behavior_on_backorder_creation": self.behavior_on_backorder_creation,
                "behavior_on_split_operation": self.behavior_on_split_operation,
                "show_product_information": self.show_product_information,
                "scan_destination_package": self.scan_destination_package,
                "confirm_source_package": self.confirm_source_package,
                "check_shipping_information": self.check_shipping_information,
                "hide_qty_to_receive": self.hide_qty_to_receive,
                "open_details_screen_first": self.open_details_screen_first,
                "quality_check_per_product_line": self.quality_check_per_product_line,
            }
        }


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_stock_picking_info(self, **kwargs):
        result = {}
        picking = self.search([("id", "=", kwargs.get("picking").get("id"))])
        if not picking:
            return result
        models = {
            "stock.picking": picking,
            "stock.move": picking.move_ids_without_package,
            "stock.move.line": picking.move_line_ids_without_package
        }
        for item in models:
            result[item] = models[item].read(fields=kwargs["picking"][item]["fields"])
        return result

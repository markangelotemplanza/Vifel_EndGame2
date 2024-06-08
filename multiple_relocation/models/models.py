# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.exceptions import ValidationError

class multiple_relocation(models.TransientModel):
    _inherit = 'stock.quant.relocate'
    

    def action_relocate_quants(self):
        # raise ValidationError(_("Another user is already created using this email"))
        self.ensure_one()
        
        for quant in self.quant_ids:
            # Retrieve the destination location ID from quant_ids.x_studio_destination_relocation field
            dest_location_id = quant.x_studio_dest_relocation
            
            # Perform relocation actions only if the destination location is set
            if dest_location_id:
                lot_ids = quant.lot_id
                product_ids = quant.product_id
                
                quant.action_clear_inventory_quantity()
                
                # Check if partial packaging is enabled and the destination package is not set
                if self.is_partial_package and not self.dest_package_id:
                    quants_to_unpack = quant.filtered(lambda q: not all(sub_q in quant.ids for sub_q in q.package_id.quant_ids.ids))
                    quants_to_unpack.move_quants(location_dest_id=dest_location_id, message=self.message, unpack=True)
                    quant -= quants_to_unpack
                
                quant.move_quants(location_dest_id=dest_location_id, package_dest_id=self.dest_package_id, message=self.message)
                
                # If there's a single lot associated with the quant, open the quants
                if self.env.context.get('default_lot_id', False) and len(lot_ids) == 1:
                    lot_ids.action_lot_open_quants()
                
                # If there's a single product associated with the quant, update the quantity on hand
                elif self.env.context.get('single_product', False) and len(product_ids) == 1:
                    product_ids.action_update_quantity_on_hand()


import logging

_logger = logging.getLogger(__name__)
class ensure_ownership(models.Model):
    _inherit = 'stock.move'
    

    def _update_reserved_quantity(self, need, location_id, quant_ids=None, lot_id=None, package_id=None, owner_id=None, strict=True):
        """ Create or update move lines and reserves quantity from quants
            Expects the need (qty to reserve) and location_id to reserve from.
            `quant_ids` can be passed as an optimization since no search on the database
            is performed and reservation is done on the passed quants set
        """

        
        self.ensure_one()
        if quant_ids is None:
            quant_ids = self.env['stock.quant']
        if not lot_id:
            lot_id = self.env['stock.lot']
        if not package_id:
            package_id = self.env['stock.quant.package']
        if not owner_id:
            owner_id = self.env['res.partner']


        
        # _logger.info(self.partner_id.name)
        quants = quant_ids._get_reserve_quantity(
            self.product_id, location_id, need, product_packaging_id=self.product_packaging_id,
            uom_id=self.product_uom, lot_id=lot_id, package_id=package_id, owner_id=self.partner_id, strict=strict)

        taken_quantity = 0
        rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # Find a candidate move line to update or create a new one.
        
        for reserved_quant, quantity, in quants:
            
            taken_quantity += quantity
            to_update = next((line for line in self.move_line_ids if line._reservation_is_updatable(quantity, reserved_quant)), False)
            if to_update:
                uom_quantity = self.product_id.uom_id._compute_quantity(quantity, to_update.product_uom_id, rounding_method='HALF-UP')
                uom_quantity = float_round(uom_quantity, precision_digits=rounding)
                uom_quantity_back_to_product_uom = to_update.product_uom_id._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            if to_update and float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                to_update.with_context(reserved_quant=reserved_quant).quantity += uom_quantity
            else:
                if self.product_id.tracking == 'serial':
                    vals_list = self._add_serial_move_line_to_vals_list(reserved_quant, quantity)
                    if vals_list:
                        self.env['stock.move.line'].with_context(reserved_quant=reserved_quant).create(vals_list)
                else:
                    self.env['stock.move.line'].with_context(reserved_quant=reserved_quant).create(self._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant))
        _logger.info('haha')
        _logger.info(str(taken_quantity))
        return taken_quantity
        

    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100


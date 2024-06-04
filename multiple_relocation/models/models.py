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



    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100


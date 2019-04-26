# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_compare, float_round


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_cancel_draft(self):
        if not len(self.ids):
            return False
        move_obj = self.env['stock.move']
        for (ids, name) in self.name_get():
            message = _("Picking '%s' has been set in draft state.") % name
            self.message_post(message)
        for pick in self:
            ids2 = [move.id for move in pick.move_lines]
            moves = move_obj.browse(ids2)
            moves.sudo().action_draft()
        return True


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.multi
    def action_cancel_quant_create(self):
        quant_obj = self.env['stock.quant']
        for move in self:
            price_unit = move.get_price_unit()
            location = move.location_id
            rounding = move.product_id.uom_id.rounding
            vals = {
                'product_id': move.product_id.id,
                'location_id': location.id,
                'qty': float_round(move.product_uom_qty, precision_rounding=rounding),
                'cost': price_unit,
                'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': move.company_id.id,
            }
            quant_obj.sudo().create(vals)
            return
        
    @api.multi
    def action_draft(self):
        res = self.write({'state': 'draft'})
        return res

    @api.multi
    def action_cancel(self):
        procurements = self.env['procurement.order']
        for move in self:
                    
            if move.picking_id.state == 'done':
            	quant_ids = move.quant_ids.ids
                pack_op = self.env['stock.pack.operation'].sudo().search([('picking_id','=',move.picking_id.id),('product_id','=',move.product_id.id)])
                for pack_op_id in pack_op: 
                    if move.picking_id.picking_type_id.code in ['outgoing','internal']:
                        for move_id in quant_ids:
                            quant_id = self.env['stock.quant'].browse(move_id)
                            if pack_op_id.location_dest_id.usage == 'customer':
                                quant_id.write({'location_id':move.location_id.id})
                            else:
                                if move_id.lot_id:
                                    quant_id.write({'location_id':move.location_id.id})
                    #incoming
                    if move.picking_id.picking_type_id.code == 'incoming':
                        for move_id in quant_ids:
                            quant_id = self.env['stock.quant'].browse(move_id)
                            for i in quant_id:
                                if i.lot_id:
                                    i.qty = 0.0
                                else:
                                    i.qty = 0.0
        self.sudo().write({'state': 'cancel', 'move_dest_id': False})
        return True



            

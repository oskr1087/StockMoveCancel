# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_compare, float_round


class MoveCancel(models.TransientModel):
    _name = 'stock.move.cancel'
    _description = 'Stock move cancel'

    delete_move = fields.Boolean(string='Eliminar los movimientos y quants relacionados seleccionados.')
    cancel_move = fields.Boolean(string='Anular los movimientos y quants relacionados seleccionados')


    @api.multi
    def action_cancel(self):
        procurements = self.env['procurement.order']
        move_obj = self.env['stock.move']
        moves = move_obj.browse(self._context.get('active_ids', []))
        for move in moves:
            if move.picking_id.state == 'done':
            	quant_ids = move.quant_ids.ids
                pack_op = self.env['stock.pack.operation'].sudo().search([('picking_id','=',move.picking_id.id),('product_id','=',move.product_id.id)])
                for pack_op_id in pack_op:
                	if move.picking_id.picking_type_id.code in ['outgoing','internal']:
                		if move.picking_id.sale_id.warehouse_id.delivery_steps == 'pick_ship':
                			if pack_op_id.location_dest_id.usage == 'customer':
                				outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_dest_id.id),('id','in',quant_ids)])
                				if outgoing_quant:
                					old_qty = outgoing_quant[0].qty
                					outgoing_quant[0].qty = old_qty - move.product_uom_qty   
        					else:
                            		            outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_id.id)])
                            		if outgoing_quant:
                    					old_qty = outgoing_quant[0].qty
                            		                outgoing_quant[0].qty = old_qty + move.product_uom_qty      
                			else:
                				outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_id.id)])
                				if outgoing_quant:
                					old_qty = outgoing_quant[0].qty
                					outgoing_quant[0].qty = old_qty + move.product_uom_qty
                	if move.picking_id.picking_type_id.code == 'incoming':
                		incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_dest_id.id)])
                		if incoming_quant:
                			old_qty = incoming_quant[0].qty
                			incoming_quant[0].qty = old_qty - move.product_uom_qty
            if move.reserved_quant_ids:
                move.sudo().quants_unreserve()
            if self.env.context.get('cancel_procurement'):
                if move.propagate:
                    pass
            else:
                if move.move_dest_id:
                    if move.propagate:
                        move.sudo().move_dest_id.action_cancel()
                    elif move.move_dest_id.state == 'waiting':
                        # If waiting, the chain will be broken and we are not sure if we can still wait for it (=> could take from stock instead)
                        move.sudo().move_dest_id.write({'state': 'confirmed'})
                if move.procurement_id:
                    procurements |= move.procurement_id
            ##### 

            move.sudo().write({'state': 'cancel', 'move_dest_id': False})
        if procurements:
            procurements.sudo().check()
        return True


    @api.multi
    def remove_move(self):
	
        # TDE DUMB: why is cancel_procuremetn in ctx we do quite nothing ?? like not updating the move ??
        procurements = self.env['procurement.order']
        move_obj = self.env['stock.move']
        moves = move_obj.browse(self._context.get('active_ids', []))
        for move in moves:
                    
            if move.picking_id.state == 'done':
            	quant_ids = move.quant_ids.ids
                pack_op = self.env['stock.pack.operation'].sudo().search([('picking_id','=',move.picking_id.id),('product_id','=',move.product_id.id)])
                for pack_op_id in pack_op:
                	if move.picking_id.picking_type_id.code in ['outgoing','internal']:
                		if move.picking_id.sale_id.warehouse_id.delivery_steps == 'pick_ship':
                			if pack_op_id.location_dest_id.usage == 'customer':
                				outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_dest_id.id),('id','in',quant_ids)])
                				if outgoing_quant:
                					old_qty = outgoing_quant[0].qty
                					outgoing_quant[0].qty = old_qty - move.product_uom_qty
#                         elif move.picking_id.picking_type_id.code in ['outgoing']:        
        					else:
                            		            outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_id.id)])
                            		if outgoing_quant:
                    					old_qty = outgoing_quant[0].qty
                            		                outgoing_quant[0].qty = old_qty + move.product_uom_qty
#                     elif move.picking_id.picking_type_id.code in ['outgoing']:        
                			else:
                				outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_id.id)])
                				if outgoing_quant:
                					old_qty = outgoing_quant[0].qty
                					outgoing_quant[0].qty = old_qty + move.product_uom_qty
                #incoming
                	if move.picking_id.picking_type_id.code == 'incoming':
                		incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_dest_id.id)])
                		if incoming_quant:
                			old_qty = incoming_quant[0].qty
                			incoming_quant[0].qty = old_qty - move.product_uom_qty
            ####
            if move.reserved_quant_ids:
                move.sudo().quants_unreserve()
            if self.env.context.get('cancel_procurement'):
                if move.propagate:
                    pass
                    # procurements.search([('move_dest_id', '=', move.id)]).cancel()
            else:
                if move.move_dest_id:
                    if move.propagate:
                        move.sudo().move_dest_id.action_cancel()
                    elif move.move_dest_id.state == 'waiting':
                        # If waiting, the chain will be broken and we are not sure if we can still wait for it (=> could take from stock instead)
                        move.sudo().move_dest_id.write({'state': 'confirmed'})
                if move.procurement_id:
                    procurements |= move.procurement_id
            ##### 

            move.sudo().write({'state': 'cancel', 'move_dest_id': False})
            move.unlink()
        if procurements:
            procurements.sudo().check()
        return True


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

    @api.multi
    def action_draft(self):
        for pick in self:
            res = pick.write({'state': 'draft'})


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.multi
    def action_cancel_draft(self):
        if not len(self.ids):
            return False
        move_obj = self.env['stock.picking']
        for move in self:
            res = move.write({'state': 'draft'})
            moves = move_obj.browse(move.picking_id.id)
            moves.sudo().action_draft()
    
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
	
        # TDE DUMB: why is cancel_procuremetn in ctx we do quite nothing ?? like not updating the move ??
        procurements = self.env['procurement.order']
        for move in self:
                    
            if move.picking_id.state == 'done':
            	quant_ids = move.quant_ids.ids
                pack_op = self.env['stock.pack.operation'].sudo().search([('picking_id','=',move.picking_id.id),('product_id','=',move.product_id.id)])
                for pack_op_id in pack_op:
                	if move.picking_id.picking_type_id.code in ['outgoing','internal']:
                		if move.picking_id.sale_id.warehouse_id.delivery_steps == 'pick_ship':
                			if pack_op_id.location_dest_id.usage == 'customer':
                				outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_dest_id.id),('id','in',quant_ids)])
                				if outgoing_quant:
                					old_qty = outgoing_quant[0].qty
                					outgoing_quant[0].qty = old_qty - move.product_uom_qty
#                         elif move.picking_id.picking_type_id.code in ['outgoing']:        
        					else:
                            		            outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_id.id)])
                            		if outgoing_quant:
                    					old_qty = outgoing_quant[0].qty
                            		                outgoing_quant[0].qty = old_qty + move.product_uom_qty
#                     elif move.picking_id.picking_type_id.code in ['outgoing']:        
                			else:
                				outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_id.id)])
                				if outgoing_quant:
                					old_qty = outgoing_quant[0].qty
                					outgoing_quant[0].qty = old_qty + move.product_uom_qty
                #incoming
                	if move.picking_id.picking_type_id.code == 'incoming':
                		incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',pack_op_id.location_dest_id.id)])
                		if incoming_quant:
                			old_qty = incoming_quant[0].qty
                			incoming_quant[0].qty = old_qty - move.product_uom_qty
            ####
            if move.reserved_quant_ids:
                move.sudo().quants_unreserve()
            if self.env.context.get('cancel_procurement'):
                if move.propagate:
                    pass
                    # procurements.search([('move_dest_id', '=', move.id)]).cancel()
            else:
                if move.move_dest_id:
                    if move.propagate:
                        move.sudo().move_dest_id.action_cancel()
                    elif move.move_dest_id.state == 'waiting':
                        # If waiting, the chain will be broken and we are not sure if we can still wait for it (=> could take from stock instead)
                        move.sudo().move_dest_id.write({'state': 'confirmed'})
                if move.procurement_id:
                    procurements |= move.procurement_id
            ##### 

        self.sudo().write({'state': 'cancel', 'move_dest_id': False})
        if procurements:
            procurements.sudo().check()
        return True



            

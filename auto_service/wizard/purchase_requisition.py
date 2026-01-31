# -*- coding: utf-8 -*-
""" Purchase Requisition """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AutoPurchaseRequisition(models.Model):
    """ Purchase Requisition """
    _name = 'auto.purchase.requisition'
    _description = 'Purchase Requisition'

    purchase_requisition_lines_ids = fields.One2many(
        'auto.purchase.requisition.lines', 'requisition_purchase_id')

    def purchase_requisition(self):
        """ Purchase Requisition """
        products = []
        for rec in self.purchase_requisition_lines_ids:
            if rec.select:
                products.append((0, 0,
                                 {
                                  'product_id': rec.product_id.id,
                                  'product_uom_id': rec.uom_id.id,
                                  'product_qty': rec.quantity
                                  }))
                self.env['purchase.requisition'].create(
                    {'line_ids': products,
                     })


class AutoPurchaseRequisitionLines(models.Model):
    """ Auto Purchase Requisition Lines """
    _name = 'auto.purchase.requisition.lines'
    _description = 'Auto Purchase Requisition Lines'

    requisition_purchase_id = fields.Many2one('auto.purchase.requisition')
    product_id = fields.Many2one('product.product')
    uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    quantity = fields.Float()
    select = fields.Boolean()

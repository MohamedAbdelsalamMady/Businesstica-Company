# -*- coding: utf-8 -*-
""" Service Name """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class ServiceName(models.Model):
    """ Service Name """
    _name = 'service.name'
    _description = 'Service Name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('product.product')
    service_type_id = fields.Many2one('service.type')
    estimated_time = fields.Float()
    service_team_id = fields.Many2one('service.team')
    spare_parts_lines_ids = fields.One2many('spare.parts.lines',
                                            'service_name_id')
    service_parts_lines_ids = fields.One2many('service.parts.lines',
                                              'service_name_id')
    @api.onchange('service_parts_lines_ids')
    def _onchange_service_parts_lines_ids(self):
        """ service_parts_lines_ids """
        self.estimated_time=0
        for rec in self.service_parts_lines_ids:
            self.estimated_time+=rec.product_qty

    def done(self):
        """ Done """
        products=[]
        pro=[]
        self.spare_parts_lines_ids.unlink()
        for d in self.service_parts_lines_ids:
            for rec in d.spare_product_ids:
                # for t in self.service_name_id.spare_parts_lines_ids:
                #     pro.append(t.product_id.id)
                # if rec.id not in pro:
                products.append((0, 0,
                                 {
                                     'product_id': rec.id,
                                     'task':d.task,
                                     'uom_id':rec.uom_id.id

                                 }))

                # for t2 in self.service_name_id.spare_parts_lines_ids:
                #     if rec.id != t2.product_id.id and rec.id in pro:
                #         t2.unlink()
                # pro=[]



        self.write(
            {
                'spare_parts_lines_ids': products})



class SpareParts(models.Model):
    """ Spare Parts """
    _name = 'spare.parts.lines'
    _description = 'Spare Parts Lines'

    service_name_id = fields.Many2one('service.name')
    product_id = fields.Many2one('product.product', domain=[
        ('type', 'in', ['consu', 'product'])])
    uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    unit_price = fields.Float()
    product_qty = fields.Float(string="Quantity", default=1)
    subtotal = fields.Float()
    task = fields.Char()

    @api.onchange('product_id')
    def _onchange_spare_product_id(self):
        """ product_id """
        self.unit_price = self.product_id.lst_price
        self.product_qty=1
        self.subtotal = self.unit_price * self.product_qty
        self.uom_id=self.product_id.uom_id.id

    @api.onchange('unit_price', 'product_qty')
    def _onchange_subtotal(self):
        """ product_id """
        self.subtotal = self.unit_price * self.product_qty


class ServicePartsLines(models.Model):
    """ Service Parts Lines """
    _name = 'service.parts.lines'
    _description = 'Service Parts Lines'

    service_name_id = fields.Many2one('service.name')
    product_id = fields.Many2one('product.product',
                                 domain=[('type', '=', 'service')])
    task = fields.Char()
    unit_price = fields.Float()
    product_qty = fields.Float(string="Quantity", default=1)
    subtotal = fields.Float()
    spare_product_ids = fields.Many2many('product.product')


    def done(self):
        """ Done """
        products=[]
        pro=[]

        for rec in self.spare_product_ids:
            for t in self.service_name_id.spare_parts_lines_ids:
                pro.append(t.product_id.id)
            if rec.id not in pro:
                products.append((0, 0,
                                 {
                                     'product_id': rec.id,

                                 }))

            for t2 in self.service_name_id.spare_parts_lines_ids:
                if rec.id != t2.product_id.id and rec.id in pro:
                    t2.unlink()
            pro=[]



        self.service_name_id.write(
            {
             'spare_parts_lines_ids': products})

    @api.onchange('product_id')
    def _onchange_service_product_id(self):
        """ product_id """
        self.unit_price = self.product_id.lst_price
        self.product_qty=1
        self.subtotal = self.unit_price * self.product_qty

    @api.onchange('unit_price', 'product_qty')
    def _onchange_subtotal(self):
        """ product_id """
        self.subtotal = self.unit_price * self.product_qty



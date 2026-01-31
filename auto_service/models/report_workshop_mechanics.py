# -*- coding: utf-8 -*-
""" Report Workshop Mechanics """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError
import odoo.addons.decimal_precision as dp


class ReportWorkshopMechanics(models.Model):
    """ Report Workshop Mechanics """
    _name = 'report.workshop.mechanics'
    _description = 'Report Workshop Mechanics'
    _rec_name ="repair_order_number"


    repair_order_number = fields.Char()
    partner_id = fields.Many2one('res.partner',string="Customer")
    car_model=fields.Many2one('car.model',string="Model")
    plate_number = fields.Char()
    date_entry = fields.Date()
    reception_engineer = fields.Char()
    customer_response = fields.Text()
    spare_parts = fields.Char()
    under_construction = fields.Char()
    experience = fields.Char()
    delivery = fields.Char()
    fff = fields.Float(digits=(16, 6))

class StockMove(models.Model):
    """ inherit Stock Move """
    _inherit = 'stock.move'



    product_uom_qty = fields.Float(
        'Demand',
        digits=None,
    recision_digits=2,
        default=1.0, required=True, states={'done': [('readonly', True)]},
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")

class MrpBomLine(models.Model):
    """ inherit Mrp Bom Line """
    _inherit = 'mrp.bom.line'

    product_qty = fields.Float(
        'Quantity090', default=1.0,recision_digits=2,
        digits=None, required=True)


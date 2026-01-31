# -*- coding: utf-8 -*-
""" Stock Move """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class StockMove(models.Model):
    """ inherit Stock Move """
    _inherit = 'stock.move'

    available_quantity = fields.Float()


class StockMoveLine(models.Model):
    """ inherit Stock Move Line """
    _inherit = 'stock.move.line'

    available_quantity = fields.Float()

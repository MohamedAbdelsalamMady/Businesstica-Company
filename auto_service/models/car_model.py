# -*- coding: utf-8 -*-
""" Car Model """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class CarModel(models.Model):
    """ Car Model """
    _name = 'car.model'
    _description = 'Car Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

# -*- coding: utf-8 -*-
""" Car Agent """
from odoo import api, fields, models, _


class CarAgent(models.Model):
    """ Car Agent """
    _name = 'car.agent'
    _description = 'Car Agent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

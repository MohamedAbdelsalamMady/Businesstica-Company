# -*- coding: utf-8 -*-
""" Car Generation """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class CarGeneration(models.Model):
    """ Car Generation """
    _name = 'car.generation'
    _description = 'Car Generation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

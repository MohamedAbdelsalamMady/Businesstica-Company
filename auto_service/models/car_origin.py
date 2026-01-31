# -*- coding: utf-8 -*-
""" Car Origin """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class CarOrigin(models.Model):
    """ Car Origin """
    _name = 'car.origin'
    _description = 'Car Origin'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

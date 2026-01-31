# -*- coding: utf-8 -*-
""" Car Body Style """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CarBodyStyle(models.Model):
    """ Car Body Style """
    _name = 'car.body.style'
    _description = 'Car Body Style'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

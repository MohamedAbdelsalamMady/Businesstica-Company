# -*- coding: utf-8 -*-
""" Car Cylinders """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class CarCylinders(models.Model):
    """ Car Cylinders """
    _name = 'car.cylinders'
    _description = 'Car Cylinders'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

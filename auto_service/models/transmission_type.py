# -*- coding: utf-8 -*-
""" Transmission Type """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class TransmissionType(models.Model):
    """ Transmission Type """
    _name = 'transmission.type'
    _description = 'Transmission Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    code = fields.Char()

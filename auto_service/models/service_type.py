# -*- coding: utf-8 -*-
""" Service Type """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class ServiceType(models.Model):
    """ Service Type """
    _name = 'service.type'
    _description = 'Service Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    code = fields.Char()

# -*- coding: utf-8 -*-
""" Engine Type """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class EngineType(models.Model):
    """ Engine Type """
    _name = 'engine.type'
    _description = 'Engine Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

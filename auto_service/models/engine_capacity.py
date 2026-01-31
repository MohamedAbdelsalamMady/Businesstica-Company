# -*- coding: utf-8 -*-
""" Engine Capacity """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class EngineCapacity(models.Model):
    """ Engine Capacity """
    _name = 'engine.capacity'
    _description = 'Engine Capacity'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

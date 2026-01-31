# -*- coding: utf-8 -*-
""" Task Location """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class TaskLocation(models.Model):
    """ Task Location """
    _name = 'task.location'
    _description = 'Task Location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    code = fields.Char()

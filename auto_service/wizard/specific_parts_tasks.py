# -*- coding: utf-8 -*-
""" Specific Parts Tasks """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError

class SpecificPartsTasks(models.TransientModel):
    """ Specific Parts Tasks """
    _name = 'specific.parts.tasks'
    _description = 'Specific Parts Tasks'



# -*- coding: utf-8 -*-
""" Service Team """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class ServiceTeam(models.Model):
    """ Service Team """
    _name = 'service.team'
    _description = 'Service Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Team Name")
    res_users_id = fields.Many2one('res.users', string="Team Manager")
    users_ids = fields.Many2many('res.users', string="Team Employees")

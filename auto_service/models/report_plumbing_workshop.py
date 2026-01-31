# -*- coding: utf-8 -*-
""" Report Plumbing Workshop """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class ReportPlumbingWorkshop(models.Model):
    """ Report Plumbing Workshop """
    _name = 'report.plumbing.workshop'
    _description = 'Report Plumbing Workshop'
    _rec_name ="repair_order_number"

    repair_order_number = fields.Char()
    partner_id = fields.Many2one('res.partner',string="Customer")
    car_model=fields.Many2one('car.model',string="Model")
    plate_number = fields.Char()
    date_entry = fields.Date()
    reception_engineer = fields.Char()
    business = fields.Text()
    Waiting_spare_parts = fields.Boolean()
    plumbing = fields.Boolean()
    paint = fields.Boolean()
    unlock_and_lock = fields.Boolean(string="Unlock and lock")
    lockout_waiting = fields.Boolean()
    delivery = fields.Boolean()

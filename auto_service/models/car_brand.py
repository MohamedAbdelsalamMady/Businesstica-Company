# -*- coding: utf-8 -*-
""" Car Brand """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class CarBrand(models.Model):
    """ Car Brand """
    _name = 'car.brand'
    _description = 'Car Brand'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)

    @api.model
    def create(self, vals):
        """ Override create() """
        # vals ={'field': value}  -> dectionary contains only new filled fields
        res= super(CarBrand, self).create(vals)
        res.code=res.name
        return res

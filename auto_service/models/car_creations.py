# -*- coding: utf-8 -*-
""" Car Creations """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CarCreations(models.Model):
    """ Car Creations """
    _name = 'car.creations'
    _description = 'Car Creations'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Chassis Number", tracking=True)
    car_brand_id = fields.Many2one('car.brand', tracking=True)
    car_model_id = fields.Many2one('car.model', tracking=True)
    car_origin_id = fields.Many2one('car.origin', tracking=True)
    car_body_style_id = fields.Many2one('car.body.style', tracking=True)
    transmission_type_id = fields.Many2one('transmission.type', tracking=True)
    engine_type_id = fields.Many2one('engine.type', tracking=True)
    engine_capacity_id = fields.Many2one('engine.capacity', tracking=True)
    car_cylinders_id = fields.Many2one('car.cylinders', tracking=True)
    maximum_power = fields.Char(string="Maximum power (HP @ RPM)", tracking=True)
    fuel_consumption = fields.Char(string="Fuel Consumption (Liter/100 KM)", tracking=True)
    car_generation_id = fields.Many2one('car.generation', tracking=True)
    license_plate_no = fields.Char(tracking=True)
    motor_number = fields.Char(tracking=True)
    top_number = fields.Char(tracking=True)
    partner_id = fields.Many2one('res.partner', string="customer", tracking=True)
    car_agent_id = fields.Many2one('car.agent', tracking=True)
    last_km = fields.Integer(tracking=True)
    date_service_now = fields.Date(tracking=True)
    service_description = fields.Text(tracking=True)
    specified_maintenance_distance = fields.Integer(tracking=True)
    car_color = fields.Char()

    @api.constrains('name')
    def unique_chassis_number(self):
        for car in self:
            if self.search_count([('name', '=', car.name)]) > 1:
                raise ValidationError("Chassis Number Must Be Unique")

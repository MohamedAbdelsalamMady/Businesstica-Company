# -*- coding: utf-8 -*-
""" Car Inspection Report """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class CarInspectionReport(models.Model):
    """ Car Inspection Report """
    _name = 'car.inspection.report'
    _description = 'Car Inspection Report'


    partner_id = fields.Many2one('res.partner',string="Customer")
    repair_order_number= fields.Char()
    chassis_no = fields.Char()
    plate_number = fields.Char()
    date = fields.Date()
    person_conducting_disclosure = fields.Char(string="The name of the person conducting the general disclosure")
    original_engine_number = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    engine_sound = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])

    engine_oil = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    transmission_oil = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    power_oil = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    brake_fluid = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    freezing_liquid = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    thongs = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    belts_car = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_drums = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    back_drums = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_staple = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    posterior_tail = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_shears = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    background_shears = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    steering_wheel_box = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    steering_wheel_bars = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])


    background_helpers = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    shakman = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    engine_bases = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    transmission_base = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    corona_sound = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    oil_leaks = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    tires = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    conditioning_hot = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    conditioning_cold = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    radio = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    interior_lighting = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    steering_wheel_case = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    case_steering_buttons = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="case of steering wheel buttons")
    front_seat_movements = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    read_odometer = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    test_result_device = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="Engine condition Test result with the device")
    airbag_system = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    transmission_system = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    rest_systems_car = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="The rest of the systems in the car")
    headlights = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    lanterns_background = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_glass = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    background_glass = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    movable_roof = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    side_mirrors = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    march_sound = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    charging_dynamo = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    battery_status = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    centerlock = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    wiper_sprinklers = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="Wipers and wiper sprinklers")

    
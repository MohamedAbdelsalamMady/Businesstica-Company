# -*- coding: utf-8 -*-
""" Project"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class ProjectProject(models.Model):
    """ inherit Project """
    _inherit = 'project.project'

    all_tasks_done = fields.Boolean()
    car_diagnoses_id = fields.Many2one('car.diagnoses')
    reception_information_id = fields.Many2one('reception.information')
    car_creations_id = fields.Many2one('car.creations',
                                       string="Chassis Number")
    license_plate_no = fields.Char()
    estimated_time = fields.Float(string="Full Estimated Time")
    auto_service_timers_id = fields.Many2one('auto.service.timers')
    time_sheet_tasks_ids = fields.One2many('time.sheet.tasks', 'project_project_id')

    def wait_to_deliver(self):
        """ Wait To Deliver """
        tasks = self.env['project.task'].search([
            ('project_id', '=', self.id)])
        self.env['wait.to.deliver'].create(
            {'reception_information_id': self.reception_information_id.id,
             'partner_id': self.reception_information_id.partner_id.id,
             'phone_number': self.reception_information_id.phone_number,
             'email': self.reception_information_id.email,
             'address': self.reception_information_id.address,
             'car_creations_id': self.reception_information_id.car_creations_id.id,
             'car_brand_id': self.reception_information_id.car_brand_id.id,
             'car_model_id': self.reception_information_id.car_model_id.id,
             'car_origin_id': self.reception_information_id.car_creations_id.car_origin_id.id,
             'car_body_style_id': self.reception_information_id.car_body_style_id.id,
             'transmission_type_id': self.reception_information_id.transmission_type_id.id,
             'engine_type_id': self.reception_information_id.engine_type_id.id,
             'engine_capacity_id': self.reception_information_id.engine_capacity_id.id,
             'car_cylinders_id': self.reception_information_id.car_cylinders_id.id,
             'maximum_power': self.reception_information_id.car_creations_id.maximum_power,
             'fuel_consumption': self.reception_information_id.car_creations_id.fuel_consumption,
             'car_generation_id': self.reception_information_id.car_generation_id.id,
             'license_plate_no': self.reception_information_id.license_plate_no,
             'motor_number': self.reception_information_id.motor_number,
             'top_number': self.reception_information_id.top_number,
             'car_agent_id': self.reception_information_id.car_agent_id.id,
             'last_km': self.reception_information_id.last_km,
             'date_service_now': self.reception_information_id.date_service_now,
             'service_description': self.reception_information_id.service_description,
             'now_km': self.reception_information_id.now_km,
             'request_ordinary_service': self.reception_information_id.request_ordinary_service,
             'service_name_id': self.reception_information_id.service_name_id.ids,
             'service_type_id': self.reception_information_id.service_type_id.id,
             'project_id': self.id,
             'project_task_ids': self.tasks.ids
             })
        self.all_tasks_done = False
        self.reception_information_id.under_progress_case='2'
        self.reception_information_id.s=False
        self.reception_information_id.show_state='1'
        self.reception_information_id.task_status='1'
        self.reception_information_id.under_progress_end=fields.Datetime.now()
        hours=self.reception_information_id.under_progress_end-self.reception_information_id.under_progress_start
        self.reception_information_id.under_progress_hours=hours
        self.reception_information_id.timer_start=fields.Datetime.now()
        self.reception_information_id.wait_deliver_state='1'
        self.reception_information_id.wait_deliver_start=fields.Datetime.now()



class TimeSheetTasks(models.Model):
    """ Time Sheet Tasks """
    _name = 'time.sheet.tasks'
    _description = 'Time Sheet Tasks'
    
    project_project_id = fields.Many2one('project.project')
    project_task_id = fields.Many2one('project.task')

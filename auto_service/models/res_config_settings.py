# -*- coding: utf-8 -*-
""" Res Config Settings """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reception_information_deadline_hours = fields.Integer(related='company_id.reception_information_deadline_hours',readonly=0)
    car_diagnoses_hours = fields.Integer(related='company_id.car_diagnoses_hours',readonly=0)
    wait_to_deliver_hours= fields.Integer(related='company_id.wait_to_deliver_hours',readonly=0)
    section_manager_hours = fields.Integer(related='company_id.section_manager_hours',readonly=0)
    manager_hours = fields.Integer(related='company_id.manager_hours',readonly=0)
    reception_information_deadline_minute = fields.Integer(related='company_id.reception_information_deadline_minute',readonly=0)
    car_diagnoses_minute = fields.Integer(related='company_id.car_diagnoses_minute',readonly=0)
    wait_to_deliver_minute= fields.Integer(related='company_id.wait_to_deliver_minute',readonly=0)
    section_manager_minute = fields.Integer(related='company_id.section_manager_minute',readonly=0)
    manager_minute = fields.Integer(related='company_id.manager_minute',readonly=0)


    @api.onchange('reception_information_deadline_minute','car_diagnoses_minute','wait_to_deliver_minute','section_manager_minute','manager_minute')
    def _onchange_reception_information_deadline_minute(self):
        """ reception_information_deadline_minute """
        if self.reception_information_deadline_minute >=59:
            raise ValidationError(
                _("Reception Information Deadline Minutes must be less than 60"))
        if self.car_diagnoses_minute >=59:
            raise ValidationError(
                _("Car Diagnoses Minutes Deadline Minutes must be less than 60"))
        if self.wait_to_deliver_minute >=59:
            raise ValidationError(
                _("Wait to Deliver Minutes Deadline Minutes must be less than 60"))
        if self.section_manager_minute >=59:
            raise ValidationError(
                _("Section Manager Minute Deadline Minutes must be less than 60"))
        if self.manager_minute >=59:
            raise ValidationError(
                _("Manager Minutes Deadline Minutes must be less than 60"))


class ResCompany(models.Model):
    """ inherit Res Company """
    _inherit = 'res.company'

    reception_information_deadline_hours = fields.Integer()
    car_diagnoses_hours = fields.Integer()
    wait_to_deliver_hours = fields.Integer()
    section_manager_hours = fields.Integer()
    manager_hours = fields.Integer()
    reception_information_deadline_minute = fields.Integer()
    car_diagnoses_minute = fields.Integer()
    wait_to_deliver_minute= fields.Integer()
    section_manager_minute = fields.Integer()
    manager_minute = fields.Integer()
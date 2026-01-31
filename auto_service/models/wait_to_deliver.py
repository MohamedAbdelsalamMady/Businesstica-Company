# -*- coding: utf-8 -*-
""" Wait To Deliver """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class WaitToDeliver(models.Model):
    """ Wait To Deliver """
    _name = 'wait.to.deliver'
    _description = 'Wait To Deliver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default='NEW',tracking=True)
    reception_information_id = fields.Many2one('reception.information',tracking=True)
    state = fields.Selection(
        [('1', 'Draft'),
         ('2', 'Delivered')],
        default='1',
        string='Status'
    )
    partner_id = fields.Many2one('res.partner', string="Customer",tracking=True)
    phone_number = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    address = fields.Char(tracking=True)
    car_creations_id = fields.Many2one('car.creations', 'Car Chassis Number')
    car_brand_id = fields.Many2one('car.brand')
    car_model_id = fields.Many2one('car.model')
    car_origin_id = fields.Many2one('car.origin')
    car_body_style_id = fields.Many2one('car.body.style')
    transmission_type_id = fields.Many2one('transmission.type')
    engine_type_id = fields.Many2one('engine.type')
    engine_capacity_id = fields.Many2one('engine.capacity')
    car_cylinders_id = fields.Many2one('car.cylinders')
    maximum_power = fields.Char(string="Maximum power (HP @ RPM)")
    fuel_consumption = fields.Char(string="Fuel Consumption (Liter/100 KM)")
    car_generation_id = fields.Many2one('car.generation')
    license_plate_no = fields.Char()
    motor_number = fields.Char()
    top_number = fields.Char()
    car_agent_id = fields.Many2one('car.agent')
    last_km = fields.Integer()
    date_service_now = fields.Date()
    service_description = fields.Text()
    now_km = fields.Integer()
    request_ordinary_service = fields.Boolean(
        string="request ordinary service ?")
    service_name_id = fields.Many2many('service.name')
    service_type_id = fields.Many2one('service.type')
    project_id = fields.Many2one('project.project')
    project_task_ids = fields.Many2many('project.task')
    # timer

    timer_start = fields.Datetime("Timer Start")
    timer_stop = fields.Float()
    timer_pause = fields.Datetime("Timer Last Pause")
    is_timer_running = fields.Boolean(compute="_compute_is_timer_running")
    res_model = fields.Char()
    res_id = fields.Integer()
    user_id = fields.Many2one('res.users')
    stop_timer = fields.Boolean()
    start_timer = fields.Boolean()
    cleaned_inside_out = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="The car has been cleaned inside and out")
    note_cleaned_inside = fields.Text()

    exterior_light_spaces = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Interior and exterior lights and spaces")
    exterior_note = fields.Text()

    mirrors = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Mirrors")
    note_mirrors = fields.Text()

    hvac_system = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="HVAC system")
    hvac_system_note = fields.Text()

    system_parking_brake = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="brake system and parking brake")
    parking_brake_note = fields.Text()
    guidance_system = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Guidance system")
    guidance_system_note = fields.Text()

    gearbox_differential = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Gearbox and Differential")
    gearbox_differential_note = fields.Text()
    front_suspension = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Front Suspension(The front furniture)")
    front_suspension_note = fields.Text()

    rear_suspension = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Rear Suspension(Background Furniture)")
    rear_suspension_note = fields.Text()
    maintenance_appointment_reactivated = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="The next maintenance appointment has been reactivated in the dashboard")
    appointment_reactivated_note = fields.Text()

    ensure_sufficient_tank = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Ensure that there are no warning messages on the dashboard and that there is sufficient water in the car's tank")
    sufficient_tank_note = fields.Text()

    verify_repair = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Verify all works mentioned in the repair order")
    verify_repair_note = fields.Text()

    mentioned_repair_appendix = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Verify all works mentioned in the repair order appendix")
    repair_appendix_note = fields.Text()
    ensure_similar_repair = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Ensure that the customer's complaint is similar to the repair process")
    similar_repair_note = fields.Text()

    oil_fluid_levels = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Check oil and fluid levels")
    oil_fluid_note = fields.Text()

    ensure_calf_torque = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Ensure that the calf is connected to the torque")
    calf_torque_note = fields.Text()

    examination_tire_kit = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Examination of the spare tire and the kit")
    tire_kit_note = fields.Text()
    check_pause_time = fields.Float()
    success_timer = fields.Float()
    s = fields.Boolean()
    task_status = fields.Selection([('1', 'On Track'), ('2', 'Late')],
                                   default='1',
                                   string='Status', tracking=True)

    @api.depends('timer_start', 'timer_pause')
    def _compute_is_timer_running(self):
        for record in self:
            record.is_timer_running = record.timer_start and not record.timer_pause

    @api.model
    def create(self, vals):
        # Reset the user_timer_id to force the recomputation
        self.env[vals['res_model']].invalidate_cache(fnames=['user_timer_id'],
                                                     ids=[vals['res_id']])
        return super().create(vals)

    def action_timer_start(self):
        if not self.timer_start:
            self.write({'timer_start': fields.Datetime.now()})

    def action_timer_stop(self):
        """ Stop the timer and return the spent minutes since it started
            :return minutes_spent if the timer is started,
                    otherwise return False
        """
        if not self.timer_start:
            return False
        minutes_spent = self._get_minutes_spent()
        self.write({'timer_stop': minutes_spent, 'timer_start': False,
                    'timer_pause': False})
        return minutes_spent

    def _get_minutes_spent(self):
        start_time = self.timer_start
        stop_time = fields.Datetime.now()
        # timer was either running or paused
        if self.timer_pause:
            start_time += (stop_time - self.timer_pause)
        return (stop_time - start_time).total_seconds() / 60

    def action_timer_pause(self):
        self.write({'timer_pause': fields.Datetime.now()})

    def action_timer_resume(self):
        new_start = self.timer_start + (
                fields.Datetime.now() - self.timer_pause)
        self.write({'timer_start': new_start, 'timer_pause': False})

    @api.model
    def create(self, vals):
        """ Override create method to sequence name """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'wait.to.deliver') or '/'
        res = super(WaitToDeliver, self).create(vals)
        res.action_timer_start()
        return res

    def show_finish(self):
        """ Show Finish """
        if not self.cleaned_inside_out or not self.exterior_light_spaces \
                or not self.mirrors or not self.hvac_system \
                or not self.system_parking_brake or not self.guidance_system \
                or not self.gearbox_differential or not self.front_suspension \
                or not self.rear_suspension or not self.maintenance_appointment_reactivated \
                or not self.ensure_sufficient_tank or not self.verify_repair \
                or not self.mentioned_repair_appendix or not self.ensure_similar_repair \
                or not self.oil_fluid_levels or not self.ensure_calf_torque or not \
                self.examination_tire_kit:
            raise ValidationError(
                _("Please complete Final Inspection Before Delivery information"))

        else:
            self.reception_information_id.is_finished = True
            self.reception_information_id.final_inspection = True
            self.reception_information_id.state = '4'
            self.reception_information_id.show_state='1'
            self.state = '2'
            self.reception_information_id.s = False
            self.reception_information_id.task_status= '1'
            self.reception_information_id.cleaned_inside_out = self.cleaned_inside_out
            self.reception_information_id.exterior_light_spaces = self.exterior_light_spaces
            self.reception_information_id.mirrors = self.mirrors
            self.reception_information_id.hvac_system = self.hvac_system
            self.reception_information_id.system_parking_brake = self.system_parking_brake
            self.reception_information_id.guidance_system = self.guidance_system
            self.reception_information_id.gearbox_differential = self.gearbox_differential
            self.reception_information_id.front_suspension = self.front_suspension
            self.reception_information_id.rear_suspension = self.rear_suspension
            self.reception_information_id.maintenance_appointment_reactivated = self.maintenance_appointment_reactivated
            self.reception_information_id.ensure_sufficient_tank = self.ensure_sufficient_tank
            self.reception_information_id.verify_repair = self.verify_repair
            self.reception_information_id.mentioned_repair_appendix = self.mentioned_repair_appendix
            self.reception_information_id.ensure_similar_repair = self.ensure_similar_repair
            self.reception_information_id.oil_fluid_levels = self.oil_fluid_levels
            self.reception_information_id.ensure_calf_torque = self.ensure_calf_torque
            self.reception_information_id.examination_tire_kit = self.examination_tire_kit
            self.reception_information_id.note_cleaned_inside = self.note_cleaned_inside
            self.reception_information_id.exterior_note = self.exterior_note
            self.reception_information_id.note_mirrors = self.note_mirrors
            self.reception_information_id.hvac_system_note = self.hvac_system_note
            self.reception_information_id.parking_brake_note = self.parking_brake_note
            self.reception_information_id.guidance_system_note = self.guidance_system_note
            self.reception_information_id.gearbox_differential_note = self.gearbox_differential_note
            self.reception_information_id.front_suspension_note = self.front_suspension_note
            self.reception_information_id.rear_suspension_note = self.rear_suspension_note
            self.reception_information_id.appointment_reactivated_note = self.appointment_reactivated_note
            self.reception_information_id.sufficient_tank_note = self.sufficient_tank_note
            self.reception_information_id.verify_repair_note = self.verify_repair_note
            self.reception_information_id.repair_appendix_note = self.repair_appendix_note
            self.reception_information_id.similar_repair_note = self.similar_repair_note
            self.reception_information_id.oil_fluid_note = self.oil_fluid_note
            self.reception_information_id.calf_torque_note = self.calf_torque_note
            self.reception_information_id.tire_kit_note = self.tire_kit_note
            self.action_timer_pause()
            self.reception_information_id.wait_deliver_end=fields.Datetime.now()
            hours=self.reception_information_id.wait_deliver_end-self.reception_information_id.wait_deliver_start
            self.reception_information_id.wait_deliver_hours=hours
            self.reception_information_id.timer_start=fields.Datetime.now()
            self.reception_information_id.s=False
            self.reception_information_id.finish_start=fields.Datetime.now()
            self.reception_information_id.finish_state='1'


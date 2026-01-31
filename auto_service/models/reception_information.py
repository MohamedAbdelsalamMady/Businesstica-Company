# -*- coding: utf-8 -*-
""" Reception Information """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError
from dateutil.relativedelta import relativedelta
import datetime
import warnings
import math


class ReceptionInformation(models.Model):
    """ Reception Information """
    _name = 'reception.information'
    _description = 'Reception Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        [('1', 'Reception'),
         ('2', 'Under Diagnose'), ('3', 'Working Under Progress'),
         ('4', 'Wait To Deliver'),
         ('6', 'Invoiced'), ('5', 'Finished'), ('7', 'cancelled & closed'), ('8', 'Inspection Transfer Ownership'),
         ('9', 'Pre-Travel Vehicle Inspection')],
        default='1',
        string='Status', tracking=True
    )
    show_state = fields.Selection(
        [('1', 'Reception'),
         ('2', 'Section Manager'), ('3', 'Manager'),
         ('4', 'Owner')],
        default='1',
        string='Status', tracking=True
    )
    name = fields.Char(default='New', tracking=True)
    user_id = fields.Many2one('res.users', string="Reception Employee",
                              default=lambda self: self.env.user, tracking=True)
    service_team_id = fields.Many2one('service.team', tracking=True)
    res_users_id = fields.Many2one('res.users', string="Team Manager",
                                   tracking=True)
    arriving_time = fields.Datetime(tracking=True)
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 tracking=True, related='car_creations_id.partner_id', readonly=0)
    phone_number = fields.Char(tracking=True, related='partner_id.mobile')
    email = fields.Char(tracking=True, related='partner_id.email')
    address = fields.Char(tracking=True, related='partner_id.street')
    license_plate_no = fields.Char(tracking=True)
    motor_number = fields.Char(tracking=True)
    top_number = fields.Char(tracking=True)
    last_date_service = fields.Date(string="Last Date Of Service",
                                    tracking=True)
    last_service_name = fields.Text(tracking=True)
    last_km = fields.Integer(tracking=True)
    now_km = fields.Integer(tracking=True)
    car_brand_id = fields.Many2one('car.brand', tracking=True)
    car_model_id = fields.Many2one('car.model', tracking=True)
    car_agent_id = fields.Many2one('car.agent', tracking=True)
    car_body_style_id = fields.Many2one('car.body.style', tracking=True)
    transmission_type_id = fields.Many2one('transmission.type', tracking=True)
    engine_type_id = fields.Many2one('engine.type', tracking=True)
    engine_capacity_id = fields.Many2one('engine.capacity', tracking=True)
    car_cylinders_id = fields.Many2one('car.cylinders', tracking=True)
    car_generation_id = fields.Many2one('car.generation', tracking=True)
    car_creations_id = fields.Many2one('car.creations',
                                       string="Chassis Number", tracking=True)
    request_ordinary_service = fields.Boolean(
        string="request ordinary service ?", tracking=True)
    service_name_id = fields.Many2many('service.name', tracking=True)
    service_type_id = fields.Many2one('service.type', tracking=True)
    receive_spare_parts = fields.Boolean(
        string="Do you want to receive old spare parts?", tracking=True)
    wash_car = fields.Boolean(
        string="Do you want to wash the car inside and out?", tracking=True)
    service_description = fields.Text(tracking=True)
    car_diagnoses_ids = fields.One2many('car.diagnoses',
                                        'reception_information_id',
                                        tracking=True)
    count_car_diagnoses = fields.Integer(compute='_compute_count_car_diagnoses',
                                         store=True, tracking=True, string="Car Diagnoses")
    date_service_now = fields.Date(default=fields.Date.today(), tracking=True)
    count_sale_orders = fields.Integer(compute='_compute_count_sale_order',
                                       store=True, tracking=True, string="Sale Orders")
    sale_order_ids = fields.One2many('sale.order', 'reception_information_id',
                                     tracking=True)
    count_invoices = fields.Integer(compute='_compute_count_invoices',
                                    store=True, tracking=True, string="Invoices")
    account_move_ids = fields.One2many('account.move',
                                       'reception_information_id',
                                       tracking=True)
    count_tasks = fields.Integer(compute='_compute_count_tasks',
                                 store=True, tracking=True, string="Tasks")
    tasks_ids = fields.One2many('project.task',
                                'reception_information_id', tracking=True)
    old_spare_parts = fields.Boolean(tracking=True)
    wash_car = fields.Boolean(tracking=True)
    # timer
    timer_start = fields.Datetime("Timer", tracking=True)
    timer_stop = fields.Float(tracking=True)
    timer_pause = fields.Datetime("Timer Last Pause", tracking=True)
    is_timer_running = fields.Boolean(compute="_compute_is_timer_running",
                                      tracking=True)
    res_model = fields.Char(tracking=True)
    res_id = fields.Integer(tracking=True)
    # TIMER STATES
    draft_state_timer = fields.Char(tracking=True)
    Finished_state_timer = fields.Char(tracking=True)
    under_diagnosis_state = fields.Char(tracking=True)
    under_progress_state = fields.Char(tracking=True)
    stop_timer = fields.Boolean(tracking=True)
    start_timer = fields.Boolean(tracking=True)
    show_pause = fields.Boolean(tracking=True)
    show_resume = fields.Boolean(tracking=True)
    is_finished = fields.Boolean(tracking=True)

    success_timer = fields.Float()
    diagnosis_timer = fields.Char()

    check_old_spare_parts = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Old Spare Parts")
    old_spare_parts_note = fields.Text()
    calf_bolts = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Calf Bolts")
    calf_bolts_note = fields.Text()
    vehicle_license_history = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Vehicle license and history")
    vehicle_license_note = fields.Text()
    car_sumps = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Car Sumps")
    car_sumps_note = fields.Text()
    dashboard_messages = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Dashboard messages")
    dashboard_messages_note = fields.Text()
    conditioning_review = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Conditioning review")
    conditioning_review_note = fields.Text()
    radio = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="The Radio")
    radio_note = fields.Text()
    wiper_blades = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Wiper blades")
    wiper_blades_note = fields.Text()
    front_windshield_review = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Front windshield review")
    front_windshield_note = fields.Text()
    north_seat_movement = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="North front seat movement")
    north_seat_movement_note = fields.Text()
    adaptation_hobbies_movement = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Adaptation hobbies movement")
    adaptation_hobbies_note = fields.Text()
    general_glass_switch = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="General glass switch")
    general_glass_switch_note = fields.Text()
    mirror_movement = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Mirror movement")
    mirror_movement_note = fields.Text()
    watch_rest_glass = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Watch the rest of the glass")
    watch_rest_glass_note = fields.Text()
    lighter_glass = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Lighter")
    lighter_note = fields.Text()
    sunroof = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Sunroof")
    sunroof_note = fields.Text()
    console_mat = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Console mat")
    console_mat_note = fields.Text()
    mouse_movement = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Mouse movement")
    mouse_movement_note = fields.Text()
    center_lock = fields.Selection(
        [('valid', 'Valid'), ('not_valid', 'Not Valid')],
        string="Center lock")
    center_lock_note = fields.Text()
    notes = fields.Text()


    img1 = fields.Binary(
        string="Images1",
    )
    img2 = fields.Binary(
        string="Images2",
    )
    img3 = fields.Binary(
        string="Images3",
    )
    img4 = fields.Binary(
        string="Images4",
    )
    img5 = fields.Binary(
        string="Images5",
    )
    img6 = fields.Binary(
        string="Images5",
    )

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
    final_inspection = fields.Boolean()
    traveled_distance = fields.Integer()
    distance_check = fields.Boolean()
    s = fields.Boolean()
    color = fields.Integer()
    task_status = fields.Selection([('1', 'On Track'), ('2', 'Late')],
                                   default='1',
                                   string='Status', tracking=True)
    check_pause_time = fields.Float()
    under_progress_case = fields.Selection([('1', 'Still Under Progress'), ('2', 'Check To Deliver')], default='1')
    draft_time = fields.Char()
    draft_time2 = fields.Datetime()
    start = fields.Datetime(default=fields.Datetime.now())
    end = fields.Datetime()
    duration = fields.Char()
    auto_service_timers_ids = fields.One2many('auto.service.timers', 'reception_information_id')
    auto_service_timers_id = fields.Many2one('auto.service.timers')
    reception_state = fields.Selection([('1', 'Reception')])
    reception_start = fields.Datetime()
    reception_end = fields.Datetime()
    reception_hours = fields.Char()
    under_diagnose_state = fields.Selection([('1', 'Under Diagnose')])
    under_diagnose_start = fields.Datetime()
    under_diagnose_end = fields.Datetime()
    under_diagnose_hours = fields.Char()
    working_progress_state = fields.Selection([('1', 'Working Under Progress')])
    under_progress_start = fields.Datetime()
    under_progress_end = fields.Datetime()
    under_progress_hours = fields.Char()
    wait_deliver_state = fields.Selection([('1', 'Wait To Deliver')])
    wait_deliver_start = fields.Datetime()
    wait_deliver_end = fields.Datetime()
    wait_deliver_hours = fields.Char()

    finish_state = fields.Selection([('1', 'Finish')])
    finish_start = fields.Datetime()
    finish_end = fields.Datetime()
    finish_hours = fields.Char()

    full_time_state = fields.Selection([('1', 'Fill Time')], default='1')
    full_time_start = fields.Datetime(default=fields.Datetime.now())
    full_time_end = fields.Datetime()
    full_time_hours = fields.Char()

    car_diagnoses_id = fields.Many2one('car.diagnoses')

    total_hours = fields.Char()

    type_of_service = fields.Selection(
        [('1', 'Service'), ('2', 'Inspection Transfer Ownership'), ('3', 'Pre-Travel Vehicle Inspection')], default='1')

    def confirm(self):
        """ Confirm """
        for rec in self:
            if rec.type_of_service == '2':
                self.env['inspection.transfer.ownership'].create(
                    {'reception_information_id': rec.id, 'partner_id': rec.partner_id.id,
                     'chassis_no': rec.car_creations_id.id, 'plate_number': rec.license_plate_no})
                rec.state = '8'

            elif rec.type_of_service == '3':
                self.env['pre.travel.vehicle.inspection'].create(
                    {'reception_information_id': rec.id, 'partner_id': rec.partner_id.id,
                     'chassis_no': rec.car_creations_id.id, 'plate_number': rec.license_plate_no})
                rec.state = '9'

    def test_dead(self):
        """ Test """
        cars_states = self.env['reception.information'].search([])
        for rec in cars_states:

            time_now = fields.Datetime.now() - rec.timer_start
            m = time_now.total_seconds() / 60

            reception_m = self.env.company.reception_information_deadline_hours * 60
            tot_reception_minute = self.env.company.reception_information_deadline_minute + reception_m

            car_diagnoses_hours_m = self.env.company.car_diagnoses_hours * 60
            tot_car_diagnoses_minute = self.env.company.car_diagnoses_minute + car_diagnoses_hours_m

            wait_to_deliver_hours_m = self.env.company.wait_to_deliver_hours * 60
            tot_wait_to_deliver_minute = self.env.company.wait_to_deliver_minute + wait_to_deliver_hours_m

            section_manager_minute = self.env.company.section_manager_hours * 60
            tot_section_manager_minute = section_manager_minute + self.env.company.section_manager_minute

            manager_minute = self.env.company.manager_hours * 60
            tot_manager_minute = manager_minute + self.env.company.manager_minute

            print("time_now.m", m)
            print("tot_reception_minute", tot_reception_minute)
            if rec.state == '1':
                if m >= tot_reception_minute:
                    print("time_now", time_now)
                    rec.s = True
                    rec.task_status = '2'
                    rec.show_state = '2'
                    if m >= tot_section_manager_minute:
                        rec.s = True
                        rec.task_status = '2'
                        rec.show_state = '3'
                        if m >= tot_manager_minute:
                            rec.s = True
                            rec.task_status = '2'
                            rec.show_state = '4'
            if rec.state == '2':
                if m >= tot_car_diagnoses_minute:
                    print("time_now", time_now)
                    rec.s = True
                    rec.task_status = '2'
                    rec.show_state = '2'
                    rec.car_diagnoses_id.task_status = '2'
                    rec.car_diagnoses_id.s = True
                    if m >= tot_section_manager_minute:
                        rec.s = True
                        rec.task_status = '2'
                        rec.show_state = '3'
                        if m >= tot_manager_minute:
                            rec.s = True
                            rec.task_status = '2'
                            rec.show_state = '4'
            if rec.state == '3' and rec.under_progress_case == '1':
                for t in rec.tasks_ids:
                    if t.timer_start:
                        time_now = fields.Datetime.now() - t.timer_start
                    task = time_now.total_seconds() / 60
                    if task >= t.estimated_time:
                        rec.s = True
                        rec.task_status = '2'
                        rec.show_state = '2'
                        t.s = True
                        t.task_status = '2'
                        if task >= tot_section_manager_minute:
                            rec.s = True
                            rec.task_status = '2'
                            rec.show_state = '3'
                            if task >= tot_manager_minute:
                                rec.s = True
                                rec.task_status = '2'
                                rec.show_state = '4'
            if rec.state == '3' and rec.under_progress_case == '2':
                if m >= tot_wait_to_deliver_minute:
                    print("time_now", time_now)
                    rec.s = True
                    rec.task_status = '2'
                    rec.show_state = '2'
                    if m >= tot_section_manager_minute:
                        rec.s = True
                        rec.task_status = '2'
                        rec.show_state = '3'
                        if m >= tot_manager_minute:
                            rec.s = True
                            rec.task_status = '2'
                            rec.show_state = '4'
            if rec.state == '4':
                if m >= tot_section_manager_minute:
                    rec.s = True
                    rec.task_status = '2'
                    rec.show_state = '3'
                    if m >= tot_manager_minute:
                        rec.s = True
                        rec.task_status = '2'
                        rec.show_state = '4'
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def memo(self):
        """ Memo """

        total_hours_reception = self.reception_end - self.reception_start
        total_under_diagnose = self.under_diagnose_end - self.under_diagnose_start
        total_under_progress = self.under_progress_end - self.under_progress_start
        total_wait_deliver = self.wait_deliver_end - self.wait_deliver_start
        total_finish = self.finish_end - self.finish_start
        total_full_time = self.full_time_end - self.full_time_start

        hours_spent = total_hours_reception + total_under_diagnose + total_under_progress + total_wait_deliver + total_finish
        self.total_hours = hours_spent
        self.full_time_hours = total_full_time
        # self.auto_service_timers_id.end = fields.Datetime.now()
        # end = self.auto_service_timers_id.end
        # start = self.auto_service_timers_id.start
        # # self.auto_service_timers_id.hours_spent = math.floor(
        # #     (end - start).seconds / 3600)
        # hours_spent = math.floor(
        #     (end - start).seconds / 3600)
        # hours_spent2 = end - start
        # self.auto_service_timers_id.hours = hours_spent2
        # hours_spent2 = end - start
        # print("uou", hours_spent)
        # print("uou2", hours_spent2)

    def toto(self):
        """ Toto """
        s = 00
        m = 00
        h = 00
        ss = 0
        mm = 0
        hh = 0

        self.end = fields.Datetime.now()
        h_start = int(self.start.strftime("%H"))
        m_start = int(self.start.strftime("%M"))
        s_start = int(self.start.strftime("%S"))

        h_end = int(self.end.strftime("%H"))
        m_end = int(self.end.strftime("%M"))
        s_end = int(self.end.strftime("%S"))

        hh0 = h_end - h_start
        if hh0 > 0:
            s0 = h_start * 60 + m_start
            e0 = h_end * 60 + m_end
            se0 = e0 - s0
            se00 = se0 % (hh0 * 60)
            if se00 > 0:
                if se0 / 60 < 1:
                    hh = 00
                    mm = se0 - (hh * 60)
                else:
                    hh = int(se0 / 60)
                    mm = se0 - (hh * 60)

            # mm=m_end-m_start
        else:
            mm = m_end - m_start
        ss = s_end - s_start

        self.duration = str(hh) + ':' + str(mm)

        # total_s=self.s_start+self.s_end
        # if  total_s>=60:
        #     m=1

        # else:
        #     ss=self.s_start+self.s_end

    _sql_constraints = [(
        'unique_timer', 'UNIQUE(res_model, res_id, user_id)',
        'Only one timer occurrence by model, record and user')]

    @api.onchange('now_km')
    def _onchange_now_km(self):
        """ now_km """
        if self.now_km < self.last_km:
            raise ValidationError(
                _("Current km must be more than Last km"))
        self.traveled_distance = self.now_km - self.last_km
        if self.traveled_distance > self.car_creations_id.specified_maintenance_distance:
            self.distance_check = True

    def _compute_state(self):
        """ Override _compute_state """
        super(StockPicking, self)._compute_state()
        for rec in self:
            if rec.state == 'done':
                rec.action_timer_stop()

    @api.depends('timer_start', 'timer_pause')
    def _compute_is_timer_running(self):
        for record in self:
            record.is_timer_running = record.timer_start and not record.timer_pause
            print("timer_start 8", self.timer_start)

    def success_timer_or_denger(self):
        """ Success Timer Or Denger """
        tot_h = 0
        tot_h_diagnoses = 0
        tot_h_task = 0
        e_m_task = 0
        tot_h_wait = 0
        mmm0 = 0
        tot_d_h = 0
        reception = self.env['reception.information'].search([])
        for record in reception:
            if record.state == '1':
                record.is_timer_running = record.timer_start and not record.timer_pause
                h = int(record.timer_start.strftime("%H"))
                m = int(record.timer_start.strftime("%M"))
                s = int(record.timer_start.strftime("%S"))
                print("H :", h, "M :", m, "S :", s)
                # record.success_timer=m
                print("record.success_timer", record.success_timer)
                check_pause_time = fields.Datetime.now()
                e_h = int(fields.Datetime.now().strftime("%H"))
                e_m = int(fields.Datetime.now().strftime("%M"))
                e_s = int(fields.Datetime.now().strftime("%S"))
                record.check_pause_time = e_m
                record.write({'check_pause_time': e_m})
                print("--H :", e_m, "--M :", e_m, "--S :", e_m)

                if (e_h - h) > 0:
                    tot_h = (e_h - h) / 60
                    total_deadline = m + tot_h
                else:
                    total_deadline = record.check_pause_time - record.success_timer
                print("print", total_deadline)
                if total_deadline > self.env.company.reception_information_deadline:
                    record.s = True
                    record.task_status = '2'
                    record.show_state = '2'
                if total_deadline > self.env.company.section_manager:
                    record.s = True
                    record.task_status = '2'
                    record.show_state = '3'
                if total_deadline > self.env.company.manager:
                    record.s = True
                    record.task_status = '2'
                    record.show_state = '4'

                h0 = int(record.timer_start.strftime("%H"))
                m0 = int(record.timer_start.strftime("%M"))
                e_h0 = int(fields.Datetime.now().strftime("%H"))
                e_m0 = int(fields.Datetime.now().strftime("%M"))
                last_day = int(record.timer_start.strftime("%d"))
                day_now = int(fields.Datetime.now().strftime("%d"))

                if day_now > last_day:
                    t_day = day_now - last_day
                    tot_d_h = t_day * 24
                hours0 = e_h0 - h0

                if h0 == e_h0:
                    mm0 = m0 + e_m0
                    if mm0 > 60:
                        mmm0 = mm0 - 60
                self.draft_time = str(self.timer_pause)
                self.draft_time = str(hours0 + tot_d_h) + ":" + str(mmm0)
                # pyautogui.hotkey('f5')

            elif record.state == '2':
                diagnoses = self.env['car.diagnoses'].search([])
                for rec in diagnoses:
                    if rec.state == '1':
                        rec.is_timer_running = rec.timer_start and not rec.timer_pause
                        h_diagnoses = int(rec.timer_start.strftime("%H"))
                        m_diagnoses = int(rec.timer_start.strftime("%M"))
                        s_diagnoses = int(rec.timer_start.strftime("%S"))
                        check_pause_time_diagnoses = fields.Datetime.now()
                        e_h_diagnoses = int(
                            fields.Datetime.now().strftime("%H"))
                        e_m_diagnoses = int(
                            fields.Datetime.now().strftime("%M"))
                        e_s_diagnoses = int(
                            fields.Datetime.now().strftime("%S"))
                        rec.write({'check_pause_time': e_m_diagnoses})
                        if (e_h_diagnoses - h_diagnoses) > 0:
                            tot_h_diagnoses = (e_h_diagnoses - h_diagnoses) / 60
                        tot_m_diagnoses = m_diagnoses + tot_h_diagnoses
                        total_deadline_diagnoses = rec.check_pause_time - rec.success_timer
                        if total_deadline_diagnoses > self.env.company.car_diagnoses:
                            record.task_status = '2'
                            rec.task_status = '2'
                            record.show_state = '2'
                            # rec.show_state = '2'
                            record.s = True
                            rec.s = True
                        if total_deadline_diagnoses > self.env.company.section_manager:
                            record.task_status = '2'
                            rec.task_status = '2'
                            record.show_state = '3'
                            # rec.show_state = '3'
                            record.s = True
                            rec.s = True
                        if total_deadline_diagnoses > self.env.company.manager:
                            record.task_status = '2'
                            rec.task_status = '2'
                            record.show_state = '4'
                            # rec.show_state = '4'
                            record.s = True
                            rec.s = True
                        # pyautogui.hotkey('f5')


            elif record.state == '3':

                if record.under_progress_case == '1':
                    for rec in record.tasks_ids:
                        rec.is_timer_running = rec.timer_start and not rec.timer_pause
                        h_task = int(rec.timer_check.strftime("%H"))
                        m_task = int(rec.timer_check.strftime("%M"))
                        s_task = int(rec.timer_check.strftime("%S"))
                        check_pause_time_task = fields.Datetime.now()
                        e_h_task = int(
                            fields.Datetime.now().strftime("%H"))
                        e_m_task = int(
                            fields.Datetime.now().strftime("%M"))
                        e_s_task = int(
                            fields.Datetime.now().strftime("%S"))
                        rec.write({'check_pause_time': e_m_task})
                        if (e_h_task - h_task) > 0:
                            tot_h_task = (e_h_task - h_task) / 60
                        tot_m_task = m_task + tot_h_task
                        total_deadline_task = rec.check_pause_time - rec.success_timer
                        if total_deadline_task > rec.estimated_time:
                            record.task_status = '2'
                            record.task_status = '2'
                            record.show_state = '2'
                            # rec.show_state = '2'
                            record.s = True
                            rec.s = True
                        if total_deadline_task > self.env.company.section_manager:
                            record.task_status = '2'
                            record.task_status = '2'
                            record.show_state = '3'
                            # rec.show_state = '3'
                            record.s = True
                            rec.s = True
                        if total_deadline_task > self.env.company.manager:
                            record.task_status = '2'
                            record.task_status = '2'
                            record.show_state = '4'
                            # rec.show_state = '4'
                            record.s = True
                            rec.s = True
                        # pyautogui.hotkey('f5')

                elif record.under_progress_case == '2':
                    wait = self.env['wait.to.deliver'].search(
                        [('reception_information_id', '=', record.id)])
                    for rec in wait:
                        rec.is_timer_running = rec.timer_start and not rec.timer_pause
                        h_wait = int(rec.timer_start.strftime("%H"))
                        m_wait = int(rec.timer_start.strftime("%M"))
                        s_wait = int(rec.timer_start.strftime("%S"))
                        check_pause_time_wait = fields.Datetime.now()
                        e_h_wait = int(
                            fields.Datetime.now().strftime("%H"))
                        e_m_wait = int(
                            fields.Datetime.now().strftime("%M"))
                        e_s_wait = int(
                            fields.Datetime.now().strftime("%S"))
                        rec.write({'check_pause_time': e_m_wait})
                        if (e_h_wait - h_wait) > 0:
                            tot_h_wait = (e_h_wait - h_wait) / 60
                        tot_m_wait = m_wait + tot_h_wait
                        total_deadline_wait = rec.check_pause_time - rec.success_timer
                        if total_deadline_wait > self.env.company.wait_to_deliver:
                            record.task_status = '2'
                            rec.task_status = '2'
                            record.show_state = '2'
                            rec.show_state = '2'
                            record.s = True
                            rec.s = True
                        if total_deadline_wait > self.env.company.section_manager:
                            record.task_status = '2'
                            rec.task_status = '2'
                            record.show_state = '3'
                            rec.show_state = '3'
                            record.s = True
                            rec.s = True
                        if total_deadline_wait > self.env.company.manager:
                            record.task_status = '2'
                            rec.task_status = '2'
                            record.show_state = '4'
                            rec.show_state = '4'
                            record.s = True
                            rec.s = True
                        # pyautogui.hotkey('f5')

    @api.model
    def create(self, vals):
        # Reset the user_timer_id to force the recomputation
        self.env[vals['res_model']].invalidate_cache(fnames=['user_timer_id'],
                                                     ids=[vals['res_id']])
        return super().create(vals)

    def action_timer_start(self):
        start = []
        if not self.timer_start:
            # start.append((0, 0,
            #               {'state': self.state,
            #                'start': fields.Datetime.now()
            #                }))
            var = self.auto_service_timers_ids.create(
                {'reception_information_id': self.id, 'state': self.state, 'start': fields.Datetime.now()}).id
            self.auto_service_timers_id = var

            self.write({'timer_start': fields.Datetime.now(), 'reception_state': '1',
                        'reception_start': fields.Datetime.now(),
                        'draft_time2': fields.Datetime.now()})
            print("timer_start 1", self.timer_start)

    def action_timer_stop(self):
        """ Stop the timer and return the spent minutes since it started
            :return minutes_spent if the timer is started,
                    otherwise return False
        """
        if not self.timer_start:
            return False
        minutes_spent = self._get_minutes_spent()
        self.write({'timer_stop': minutes_spent,
                    'timer_pause': False})
        return minutes_spent

    def _get_minutes_spent(self):
        start_time = self.timer_start
        stop_time = fields.Datetime.now()
        # timer was either running or paused
        if self.timer_pause:
            start_time += (stop_time - self.timer_pause)
        print("timer_start 3", self.timer_start)
        return (stop_time - start_time).total_seconds() / 60

    def action_timer_pause(self):

        self.write({'timer_pause': fields.Datetime.now(), 'show_pause': False,
                    'show_resume': True})
        print("timer_start 6", self.timer_start)

    def action_timer_resume(self):
        new_start = self.timer_start + (
                fields.Datetime.now() - self.timer_pause)
        self.write(
            {'timer_start': new_start, 'timer_pause': False, 'show_pause': True,
             'show_resume': False})
        print("timer_start 4", self.timer_start)

    @api.model
    def get_server_time(self):
        """ Returns the server time.
            The timer widget needs the server time instead of the client time
            to avoid time desynchronization issues like the timer beginning at 0:00
            and not 23:59 and so on.
        """
        print("timer_start 7", self.timer_start)
        return fields.Datetime.now()

    # @api.constrains('car_creations_id')
    # def _check_car_creations_id(self):
    #     """ Validate car_creations_id """
    #
    #     if self.car_creations_id:
    #         reception = self.env['reception.information'].search(
    #             [('state', 'in', ['1', '2', '3', '4', '5', '6']),
    #              ('car_creations_id', '=', self.car_creations_id.id),
    #              ('id', '!=', self.id)
    #              ])
    #         if reception:
    #             return {
    #
    #                 'warning': {
    #
    #                     'title': 'Warning!',
    #
    #                     'message': 'The warning text'}
    #
    #             }

    @api.onchange('car_creations_id')
    def _onchange_car_creations_id(self):
        """ car_creations_id """
        if self.car_creations_id:
            self.car_brand_id = self.car_creations_id.car_brand_id.id
            self.car_model_id = self.car_creations_id.car_model_id.id
            self.car_body_style_id = self.car_creations_id.car_body_style_id.id
            self.transmission_type_id = self.car_creations_id.transmission_type_id.id
            self.engine_type_id = self.car_creations_id.engine_type_id.id
            self.engine_capacity_id = self.car_creations_id.engine_capacity_id.id
            self.car_cylinders_id = self.car_creations_id.car_cylinders_id.id
            self.car_generation_id = self.car_creations_id.car_generation_id.id
            self.license_plate_no = self.car_creations_id.license_plate_no
            self.motor_number = self.car_creations_id.motor_number
            self.top_number = self.car_creations_id.top_number
            self.partner_id = self.car_creations_id.partner_id.id
            self.phone_number = self.car_creations_id.partner_id.mobile
            self.email = self.car_creations_id.partner_id.email
            self.address = self.car_creations_id.partner_id.street
            self.car_agent_id = self.car_creations_id.car_agent_id.id
            self.last_date_service = self.car_creations_id.date_service_now
            self.last_km = self.car_creations_id.last_km
            self.last_service_name = self.car_creations_id.service_description
            reception = self.env['reception.information'].search(
                [('state', 'in', ['1', '2', '3', '4', '5', '6']),
                 ('car_creations_id', '=', self.car_creations_id.id)
                 ])
            if reception:
                return {

                    'warning': {

                        'title': 'Warning!',

                        'message': 'This car has an open mission'}

                }



        else:
            self.car_brand_id = self.car_creations_id.car_brand_id.id
            self.car_model_id = self.car_creations_id.car_model_id.id
            self.car_body_style_id = self.car_creations_id.car_body_style_id.id
            self.transmission_type_id = self.car_creations_id.transmission_type_id.id
            self.engine_type_id = self.car_creations_id.engine_type_id.id
            self.engine_capacity_id = self.car_creations_id.engine_capacity_id.id
            self.car_cylinders_id = self.car_creations_id.car_cylinders_id.id
            self.car_generation_id = self.car_creations_id.car_generation_id.id
            self.license_plate_no = self.car_creations_id.license_plate_no
            self.motor_number = self.car_creations_id.motor_number
            self.top_number = self.car_creations_id.top_number
            self.partner_id = self.car_creations_id.partner_id.id
            self.phone_number = self.car_creations_id.partner_id.mobile
            self.email = self.car_creations_id.partner_id.email
            self.address = self.car_creations_id.partner_id.street
            self.car_agent_id = self.car_creations_id.car_agent_id.id
            self.last_date_service = self.car_creations_id.date_service_now
            self.last_km = self.car_creations_id.last_km
            self.last_service_name = self.car_creations_id.service_description

    @api.onchange('service_team_id')
    def _onchange_service_team_id(self):
        """ service_team_id """
        self.res_users_id = self.service_team_id.res_users_id.id

    @api.depends('car_diagnoses_ids')
    def _compute_count_car_diagnoses(self):
        """ Compute count_count_car_diagnoses value """
        for rec in self:
            rec.count_car_diagnoses = len(rec.car_diagnoses_ids.ids)

    @api.depends('sale_order_ids')
    def _compute_count_sale_order(self):
        """ Compute count_count_car_diagnoses value """
        for rec in self:
            rec.count_sale_orders = len(rec.sale_order_ids.ids)

    @api.depends('account_move_ids')
    def _compute_count_invoices(self):
        """ Compute count_count_car_diagnoses value """
        for rec in self:
            rec.count_invoices = len(rec.account_move_ids.ids)

    @api.depends('tasks_ids')
    def _compute_count_tasks(self):
        """ Compute count_count_car_diagnoses value """
        for rec in self:
            rec.count_tasks = len(rec.tasks_ids.ids)

    def action_view_car_diagnoses(self):
        """ Smart button to run action """
        services = []
        spares = []
        if self.request_ordinary_service:
            for rec in self.service_name_id:
                if rec.service_parts_lines_ids:
                    for ser in rec.service_parts_lines_ids:
                        services.append((0, 0,
                                         {'product_id': ser.product_id.id,
                                          'unit_price': ser.unit_price,
                                          'product_qty': ser.product_qty,
                                          'subtotal': ser.subtotal,
                                          }))
                if rec.spare_parts_lines_ids:
                    for spr in rec.spare_parts_lines_ids:
                        spares.append((0, 0,
                                       {'product_id': spr.product_id.id,
                                        'unit_price': spr.unit_price,
                                        'product_qty': spr.product_qty,
                                        'subtotal': spr.subtotal,
                                        }))

        recs = self.mapped('car_diagnoses_ids')
        action = \
            self.env.ref(
                'auto_service.car_diagnoses_action').read()[
                0]
        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'spare_parts_diagnoses_ids': spares,
                                 'service_parts_diagnoses_ids': services,
                                 'service_description': self.service_description}

        elif len(recs) == 1:
            action['views'] = [
                (
                    self.env.ref('auto_service.car_diagnoses_form').id,
                    'form')]
            action['res_id'] = recs.ids[0]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'spare_parts_diagnoses_ids': spares,
                                 'service_parts_diagnoses_ids': services,
                                 'service_description': self.service_description}
        else:
            action['views'] = [
                (
                    self.env.ref('auto_service.car_diagnoses_form').id,
                    'form')]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'spare_parts_diagnoses_ids': spares,
                                 'service_parts_diagnoses_ids': services,
                                 'service_description': self.service_description}

        return action

    def create_diagnoses(self):
        """ Create Diagnoses """
        services = []
        spares = []
        estimated_time = 0

        s = 00
        m = 00
        h = 00
        ss = 0
        mm = 0
        hh = 0
        if not self.check_old_spare_parts or not self.calf_bolts \
                or not self.vehicle_license_history or not self.car_sumps \
                or not self.dashboard_messages or not self.conditioning_review \
                or not self.radio or not self.wiper_blades \
                or not self.front_windshield_review \
                or not self.north_seat_movement \
                or not self.adaptation_hobbies_movement \
                or not self.general_glass_switch or \
                not self.mirror_movement \
                or not self.watch_rest_glass \
                or not self.lighter_glass \
                or not self.sunroof \
                or not self.console_mat \
                or not self.mouse_movement or not self.center_lock:
            raise ValidationError(
                _("Please complete First inspection of the car information"))
        else:
            if self.request_ordinary_service:
                for rec in self.service_name_id:
                    estimated_time += rec.estimated_time
                    services.append((0, 0,
                                     {'product_id': rec.name.id,
                                      'service_name_id': rec.id,
                                      'unit_price': rec.name.list_price,
                                      'product_qty': rec.estimated_time,
                                      # 'subtotal': ser.subtotal,
                                      'service_name': rec.name.name,
                                      }))
                    # if rec.service_parts_lines_ids:
                    #     for ser in rec.service_parts_lines_ids:
                    #         services.append((0, 0,
                    #                          {'product_id': ser.product_id.id,
                    #                           'unit_price': ser.unit_price,
                    #                           'product_qty': ser.product_qty,
                    #                           'subtotal': ser.subtotal,
                    #                           'service_name': rec.name.name,
                    #                           }))
                    if rec.spare_parts_lines_ids:
                        for spr in rec.spare_parts_lines_ids:
                            spares.append((0, 0,
                                           {'product_id': spr.product_id.id,
                                            'task': spr.task,
                                            'uom_id': spr.uom_id.id,
                                            'unit_price': spr.unit_price,
                                            'product_qty': spr.product_qty,
                                            'subtotal': spr.subtotal,
                                            'service_name': rec.name.name,
                                            }))

                var = self.auto_service_timers_ids.create(
                    {'reception_information_id': self.id, 'state': '2', 'start': fields.Datetime.now()}).id
                self.car_diagnoses_id = self.env['car.diagnoses'].create(
                    {'reception_information_id': self.id,
                     'partner_id': self.partner_id.id,
                     'car_creations_id': self.car_creations_id.id,
                     'spare_parts_diagnoses_ids': spares,
                     'service_parts_diagnoses_ids': services,
                     'service_description': self.service_description,
                     'license_plate_no': self.license_plate_no,
                     'estimated_time': estimated_time,
                     'auto_service_timers_id': var
                     }).id
                self.state = '2'
                self.task_status = '1'
                self.s = False
                self.show_state = '1'
                self.end = fields.Datetime.now()
                # self.action_timer_pause()
                self.auto_service_timers_id.end = fields.Datetime.now()
                end = self.auto_service_timers_id.end
                start = self.auto_service_timers_id.start
                hours_spent = end - start
                self.auto_service_timers_id.hours = hours_spent
                # self.action_timer_start()
                self.reception_end = fields.Datetime.now()
                self.reception_hours = hours_spent
                self.under_diagnose_state = '1'
                self.under_diagnose_start = fields.Datetime.now()
                self.timer_start = fields.Datetime.now()
                h_start = int(self.start.strftime("%H"))
                m_start = int(self.start.strftime("%M"))
                s_start = int(self.start.strftime("%S"))

                h_end = int(self.end.strftime("%H"))
                m_end = int(self.end.strftime("%M"))
                s_end = int(self.end.strftime("%S"))

                hh0 = h_end - h_start
                if hh0 > 0:
                    s0 = h_start * 60 + m_start
                    e0 = h_end * 60 + m_end
                    se0 = e0 - s0
                    se00 = se0 % (hh0 * 60)
                    if se00 > 0:
                        if se0 / 60 < 1:
                            hh = 00
                            mm = se0 - (hh * 60)
                        else:
                            hh = int(se0 / 60)
                            mm = se0 - (hh * 60)

                    # mm=m_end-m_start
                else:
                    mm = m_end - m_start
                ss = s_end - s_start

                self.duration = str(hh) + ':' + str(mm)
            else:
                var = self.auto_service_timers_ids.create(
                    {'reception_information_id': self.id, 'state': '2', 'start': fields.Datetime.now()}).id
                self.car_diagnoses_id = self.env['car.diagnoses'].create(
                    {'reception_information_id': self.id,
                     'partner_id': self.partner_id.id,
                     'car_creations_id': self.car_creations_id.id,
                     'service_description': self.service_description,
                     'license_plate_no': self.license_plate_no,
                     'auto_service_timers_id': var}).id
                self.state = '2'
                self.task_status = '1'
                self.s = False
                self.show_state = '1'
                # self.action_timer_pause()

                self.auto_service_timers_id.end = fields.Datetime.now()
                end = self.auto_service_timers_id.end
                start = self.auto_service_timers_id.start
                hours_spent = end - start
                self.auto_service_timers_id.hours = hours_spent
                self.reception_end = fields.Datetime.now()
                self.reception_hours = hours_spent
                self.under_diagnose_state = '1'

                self.under_diagnose_start = fields.Datetime.now()

                # self.action_timer_start()
                self.timer_start = fields.Datetime.now()
                self.end = fields.Datetime.now()
                h_start = int(self.start.strftime("%H"))
                m_start = int(self.start.strftime("%M"))
                s_start = int(self.start.strftime("%S"))

                h_end = int(self.end.strftime("%H"))
                m_end = int(self.end.strftime("%M"))
                s_end = int(self.end.strftime("%S"))

                hh0 = h_end - h_start
                if hh0 > 0:
                    s0 = h_start * 60 + m_start
                    e0 = h_end * 60 + m_end
                    se0 = e0 - s0
                    se00 = se0 % (hh0 * 60)
                    if se00 > 0:
                        if se0 / 60 < 1:
                            hh = 00
                            mm = se0 - (hh * 60)
                        else:
                            hh = int(se0 / 60)
                            mm = se0 - (hh * 60)

                    # mm=m_end-m_start
                else:
                    mm = m_end - m_start
                ss = s_end - s_start

                self.duration = str(hh) + ':' + str(mm)

    @api.model
    def create(self, vals):
        """ Override create method to sequence name """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'reception.information') or '/'
        res = super(ReceptionInformation, self).create(vals)
        res.car_creations_id.date_service_now = res.date_service_now
        res.car_creations_id.last_km = res.now_km
        res.car_creations_id.service_description = res.service_description
        res.action_timer_start()
        res.start_timer = True
        res.show_pause = True
        res.show_resume = False
        m = int(res.timer_start.strftime("%M"))
        res.success_timer = m

        return res

    def finished(self):
        """ Finished """
        self.state = '5'
        self.is_finished = False
        self.action_timer_pause()
        self.stop_timer = True
        self.show_pause = False
        self.show_resume = False
        self.finish_end = fields.Datetime.now()
        hours = self.finish_end - self.finish_start
        self.finish_hours = hours
        self.full_time_end = fields.Datetime.now()
        self.car_diagnoses_id.state = '4'
        self.memo()


    def cancel(self):
        """ Cancel """
        sale = self.env['sale.order'].search(
            [('car_diagnoses_id', '=', self.id)])
        for s in sale:
            s.state = 'cancel'
        moves = self.env['account.move'].search(
            [('car_diagnoses_id', '=', self.id)])
        for m in moves:
            m.state = 'cancel'
        self.state = '7'

    def action_view_car_sale_orders(self):
        """ Smart button to run action """
        recs = self.env['sale.order'].search(
            [('reception_information_id', '=', self.id)])
        action = \
            self.env.ref(
                'sale.action_quotations_with_onboarding').read()[
                0]
        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description}

        elif len(recs) == 1:
            action['views'] = [
                (
                    self.env.ref('sale.view_order_form').id,
                    'form')]
            action['res_id'] = recs.ids[0]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description}
        else:
            action['views'] = [
                (
                    self.env.ref('sale.view_order_form').id,
                    'form')]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description}

        return action

    def action_view_car_account_move(self):
        """ Smart button to run action """
        recs = self.env['account.move'].search(
            [('reception_information_id', '=', self.id)])
        action = \
            self.env.ref(
                'account.action_move_out_invoice_type').read()[
                0]
        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description}

        elif len(recs) == 1:
            action['views'] = [
                (
                    self.env.ref('account.view_move_form').id,
                    'form')]
            action['res_id'] = recs.ids[0]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description}
        else:
            action['views'] = [
                (
                    self.env.ref('account.view_move_form').id,
                    'form')]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description}

        return action

    def action_view_car_project_task(self):
        """ Smart button to run action """
        recs = self.env['project.task'].search(
            [('reception_information_id', '=', self.id)])
        action = \
            self.env.ref(
                'project.act_project_project_2_project_task_all').read()[
                0]
        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id}

        elif len(recs) == 1:
            action['views'] = [
                (
                    self.env.ref('project.view_task_form2').id,
                    'form')]
            action['res_id'] = recs.ids[0]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id}
        else:
            action['views'] = [
                (
                    self.env.ref('project.view_task_form2').id,
                    'form')]
            action['context'] = {'reception_information_id': self.id,
                                 'partner_id': self.partner_id.id,
                                 'car_creations_id': self.car_creations_id.id}

        return action


class AutoServiceTimers(models.Model):
    """ Auto Service Timers """
    _name = 'auto.service.timers'
    _description = 'Auto Service Timers'

    reception_information_id = fields.Many2one('reception.information')

    state = fields.Selection(
        [('1', 'Reception'),
         ('2', 'Under Diagnose'), ('3', 'Working Under Progress'),
         ('4', 'Wait To Deliver'),
         ('6', 'Invoiced'), ('5', 'Finished'), ('7', 'cancelled & closed')],
        string='Status'
    )
    start = fields.Datetime()
    end = fields.Datetime()
    hours = fields.Char(string="Time Out")

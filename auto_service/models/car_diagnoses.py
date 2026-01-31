# -*- coding: utf-8 -*-
""" Car Diagnoses """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class CarDiagnoses(models.Model):
    """ Car Diagnoses """
    _name = 'car.diagnoses'
    _description = 'Car Diagnoses'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        [('1', 'Draft'),
         ('2', 'Sale Order Created'), ('3', 'Project Created'),('4', 'Car Finished')],
        default='1',
        string='Status', tracking=True
    )
    name = fields.Char(default='NEW', tracking=True)
    date = fields.Datetime(default=fields.Datetime.now, tracking=True)
    reception_information_id = fields.Many2one('reception.information', tracking=True)
    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True)
    car_creations_id = fields.Many2one('car.creations',
                                       string="Chassis Number", tracking=True)
    car_color=fields.Char(related='car_creations_id.car_color')

    license_plate_no = fields.Char(tracking=True)
    spare_parts_diagnoses_ids = fields.One2many('spare.parts.diagnoses',
                                                'car_diagnoses_id', tracking=True)
    service_parts_diagnoses_ids = fields.One2many('service.parts.diagnoses',
                                                  'car_diagnoses_id', tracking=True)
    service_description = fields.Text(tracking=True)
    count_sale_order = fields.Integer(compute='_compute_count_sale_order',
                                      store=True, tracking=True)
    sale_order_ids = fields.One2many('sale.order', 'car_diagnoses_id', tracking=True)
    sale_order_confirmed = fields.Boolean(tracking=True)
    project_id = fields.Many2one('project.project', tracking=True)
    timer_start = fields.Datetime("Timer Start", tracking=True)
    timer_stop = fields.Float(tracking=True)
    timer_pause = fields.Datetime("Timer Last Pause", tracking=True)
    is_timer_running = fields.Boolean(compute="_compute_is_timer_running", tracking=True)
    res_model = fields.Char(tracking=True)
    res_id = fields.Integer(tracking=True)
    user_id = fields.Many2one('res.users', tracking=True)
    assign_user_id = fields.Many2one('res.users', tracking=True,string="Assign To")
    stop_timer = fields.Boolean(tracking=True)
    start_timer = fields.Boolean(tracking=True)
    pricing_count = fields.Integer(tracking=True)
    check_pause_time = fields.Float()
    success_timer = fields.Float()
    s = fields.Boolean()
    task_status = fields.Selection([('1', 'On Track'), ('2', 'Late')],
                                   default='1',
                                   string='Status', tracking=True)
    estimated_time = fields.Float(string="Full Estimated Time")
    task = fields.Char()
    auto_service_timers_id = fields.Many2one('auto.service.timers')
    new_diagnoses_items_ids = fields.One2many('new.diagnoses.items', 'car_diagnoses_id')

    def action_view_pricing(self):
        """ Smart button to run action """
        recs = self.env['pricing'].search(
            [('car_diagnoses_id', '=',
              self.id)])
        action = self.env.ref('auto_service.pricing_action').sudo().read()[0]
        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]
            # action['context'] = {
            #     'default_project_file_id': self.project_file_id.id,
            #     'default_user_id': self.env.user.id,
            #     'default_field_study_id': self.id,
            #     'default_project_name': self.project_name,
            #     'default_business_item': self.description,
            #     'default_initial_products_ids': products}
        elif len(recs) == 1:
            action['views'] = [
                (self.env.ref('auto_service.pricing_form').id, 'form')]
            action['res_id'] = recs.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def create_new_items(self):
        """ Smart button to run action """


        action = self.env.ref('auto_service.new_diagnoses_items_wizard_action').sudo().read()[
                0]

        return action


    def view_action_send_to_pricing(self):
        """ View Action Send To Pricing """
        products = []
        for rec in self.spare_parts_diagnoses_ids:
            if rec.product_id:
                products.append((0, 0,
                                 {'product_id': rec.product_id.id,
                                  'uom_id': rec.uom_id.id,
                                  'planned_quantity': rec.product_qty,
                                  'unit_cost_price': rec.unit_price,
                                  'spare_parts_diagnoses_id': rec.id
                                  }))

        action = self.env.ref('auto_service.send_to_pricing_action').sudo().read()[
            0]
        action['views'] = [
            (self.env.ref('auto_service.send_to_pricing_form').id, 'form')]
        action['context'] = {'default_send_to_pricing_line_ids': products}

        return action

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

    @api.model
    def create(self, vals):
        """ Override create method to sequence name """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'car.diagnoses') or '/'
        res = super(CarDiagnoses, self).create(vals)
        res.action_timer_start()
        for p in res.spare_parts_diagnoses_ids:
            quantity = self.env['stock.quant'].search([
                ('product_id', '=', p.product_id.id),
                ('location_id.usage', '=', 'internal')
            ], limit=1)
            p.available_quantity = quantity.inventory_quantity_auto_apply
        m = int(res.timer_start.strftime("%M"))
        res.success_timer = m
        return res

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

    @api.depends('sale_order_ids')
    def _compute_count_sale_order(self):
        """ Compute count_sale_order value """
        for rec in self:
            rec.count_sale_order = len(rec.sale_order_ids.ids)

    def action_view_sale_orders_diagnoses(self):
        """ Smart button to run action """
        products = []
        for rec in self:
            if rec.service_parts_diagnoses_ids:
                for ser in rec.service_parts_diagnoses_ids:
                    products.append((0, 0,
                                     {'product_id': ser.product_id.id,
                                      'product_uom': ser.product_id.uom_id.id,
                                      'price_unit': ser.unit_price,
                                      'product_uom_qty': ser.product_qty,
                                      'price_subtotal': ser.subtotal,
                                      }))
            if rec.spare_parts_diagnoses_ids:
                for spr in rec.spare_parts_diagnoses_ids:
                    products.append((0, 0,
                                     {'product_id': spr.product_id.id,
                                      'product_uom': spr.product_id.uom_id.id,
                                      'price_unit': spr.unit_price,
                                      'product_uom_qty': spr.product_qty,
                                      'price_subtotal': spr.subtotal,
                                      }))

        recs = self.mapped('sale_order_ids')
        action = \
            self.env.ref(
                'sale.action_quotations_with_onboarding').read()[
                0]
        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]
            action['context'] = {'car_diagnoses_id': self.id,
                                 'reception_information_id': self.reception_information_id.id,
                                 'partner_id': self.partner_id.id,
                                 'from_car_diagnoses': True,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description,
                                 'order_line': products}

        elif len(recs) == 1:
            action['views'] = [
                (
                    self.env.ref('sale.view_order_form').id,
                    'form')]
            action['res_id'] = recs.ids[0]
            action['context'] = {'car_diagnoses_id': self.id,
                                 'reception_information_id': self.reception_information_id.id,
                                 'partner_id': self.partner_id.id,
                                 'from_car_diagnoses': True,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description,
                                 'order_line': products}
        else:
            action['views'] = [
                (
                    self.env.ref('	sale.view_order_form').id,
                    'form')]
            action['context'] = {'car_diagnoses_id': self.id,
                                 'reception_information_id': self.reception_information_id.id,
                                 'partner_id': self.partner_id.id,
                                 'from_car_diagnoses': True,
                                 'car_creations_id': self.car_creations_id.id,
                                 'service_description': self.service_description,
                                 'order_line': products}

        return action

    def create_sale_order(self):
        """ Create Sale Order """
        products = []
        for rec in self:
            if rec.service_parts_diagnoses_ids:
                for ser in rec.service_parts_diagnoses_ids:
                    products.append((0, 0,
                                     {'product_id': ser.product_id.id,
                                      'product_uom': ser.product_id.uom_id.id,
                                      'price_unit': ser.unit_price,
                                      'product_uom_qty': 1,
                                      'price_subtotal': ser.subtotal,
                                      }))
            if rec.spare_parts_diagnoses_ids:
                for spr in rec.spare_parts_diagnoses_ids:
                    products.append((0, 0,
                                     {'product_id': spr.product_id.id,
                                      'product_uom': spr.product_id.uom_id.id,
                                      'price_unit': spr.unit_price,
                                      'product_uom_qty': spr.product_qty,
                                      'price_subtotal': spr.subtotal,
                                      }))
        self.env['sale.order'].create(
            {'car_diagnoses_id': self.id,
             'reception_information_id': self.reception_information_id.id,
             'partner_id': self.partner_id.id,
             'from_car_diagnoses': True,
             'car_creations_id': self.car_creations_id.id,
             'service_description': self.service_description,
             'order_line': products})
        self.state = '2'
        self.action_timer_pause()
        self.reception_information_id.diagnosis_timer = self.timer_pause
        self.auto_service_timers_id.end = fields.Datetime.now()
        end = self.auto_service_timers_id.end
        start = self.auto_service_timers_id.start
        hours_spent = end - start
        self.auto_service_timers_id.hours = hours_spent
        self.reception_information_id.under_diagnose_end = fields.Datetime.now()
        self.reception_information_id.under_diagnose_hours = hours_spent
        self.reception_information_id.timer_start = fields.Datetime.now()
        self.reception_information_id.s = False
        self.reception_information_id.task_status = '1'
        self.reception_information_id.show_state = '1'

    def create_project_and_tasks(self):
        """ Create Project And Tasks """
        timesheet = 0
        tasks = []
        task_products = []

        for rec in self:

            if rec.service_parts_diagnoses_ids:
                for ser in rec.service_parts_diagnoses_ids:

                    for s in ser.service_name_id.service_parts_lines_ids:
                        for spar in rec.spare_parts_diagnoses_ids:
                            if s.task == spar.task:
                                task_products.append((0, 0,
                                                      {'product_id': spar.product_id.id,
                                                       # 'unit_price':ser.unit_price,
                                                       'product_qty': spar.product_qty,
                                                       'uom_id': spar.uom_id.id,
                                                       # 'subtotal': ser.subtotal,
                                                       # 'available_quantity': ser.available_quantity,

                                                       }))

                        # for serv in rec.service_parts_diagnoses_ids:
                        #     timesheet += serv.product_qty

                        tasks.append((0, 0,
                                      {'name': s.task,
                                       'car_diagnoses_id': self.id,
                                       'planned_hours': s.product_qty,
                                       'reception_information_id': self.reception_information_id.id,
                                       'service_name': ser.service_name,
                                       'estimated_time': s.product_qty,
                                       'spare_parts_task_ids': task_products

                                       }))
                        task_products = []
        var = self.reception_information_id.auto_service_timers_ids.create(
            {'reception_information_id': self.reception_information_id.id, 'state': '3',
             'start': fields.Datetime.now()}).id
        self.project_id = self.env['project.project'].create(
            {
                'name': str(self.car_creations_id.name or "") + "/" + str(self.reception_information_id.name or ""),
                'partner_id': self.partner_id.id, 'car_diagnoses_id': self.id,
                'reception_information_id': self.reception_information_id.id,
                'car_creations_id': self.car_creations_id.id,
                'license_plate_no': self.license_plate_no,
                'estimated_time': self.estimated_time,
                'task_ids': tasks,
                'auto_service_timers_id': var}).id
        self.reception_information_id.state = '3'
        self.reception_information_id.task_status = '1'
        self.reception_information_id.under_progress_case = '1'
        self.state = '3'
        self.reception_information_id.s = False
        self.reception_information_id.show_state = '1'
        self.reception_information_id.working_progress_state = '1'
        self.reception_information_id.under_progress_start = fields.Datetime.now()
        self.reception_information_id.timer_start = fields.Datetime.now()


class SparePartsDiagnoses(models.Model):
    """ Spare Parts Diagnoses """
    _name = 'spare.parts.diagnoses'
    _description = 'Spare Parts Diagnoses'

    car_diagnoses_id = fields.Many2one('car.diagnoses')
    product_id = fields.Many2one('product.product', domain=[
        ('type', 'in', ['consu', 'product'])])
    unit_price = fields.Float()
    product_qty = fields.Float(string="Quantity", default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    subtotal = fields.Float()
    available_quantity = fields.Float()
    service_name = fields.Char()
    task = fields.Char()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ product_id """
        self.unit_price = self.product_id.lst_price
        self.uom_id = self.product_id.uom_id.id
        self.product_qty = 1
        self.subtotal = self.unit_price * self.product_qty
        for p in self:
            quantity = self.env['stock.quant'].search([
                ('product_id', '=', p.product_id.id),
                ('location_id.usage', '=', 'internal')
            ])
            p.available_quantity = quantity.inventory_quantity_auto_apply

    @api.onchange('unit_price', 'product_qty')
    def _onchange_subtotal(self):
        """ product_id """
        self.subtotal = self.unit_price * self.product_qty


class ServicePartsDiagnoses(models.Model):
    """ Service Parts Diagnoses """
    _name = 'service.parts.diagnoses'
    _description = 'Service Parts Diagnoses'

    car_diagnoses_id = fields.Many2one('car.diagnoses')
    service_name_id = fields.Many2one('service.name')
    product_id = fields.Many2one('product.product', domain=[
        ('type', '=', 'service')], string="Service Name")
    unit_price = fields.Float()
    product_qty = fields.Float(string="Quantity", default=1)
    subtotal = fields.Float()
    service_name = fields.Char()

    @api.onchange('product_id')
    def _onchange_service_product_id(self):
        """ product_id """
        self.unit_price = self.product_id.lst_price
        self.product_qty = 1
        self.subtotal = self.unit_price * self.product_qty

    @api.onchange('unit_price', 'product_qty')
    def _onchange_subtotal(self):
        """ product_id """
        self.subtotal = self.unit_price * self.product_qty


class NewDiagnoses(models.Model):
    """ New Diagnoses """
    _name = 'new.diagnoses.items'
    _description = 'New Diagnoses'

    car_diagnoses_id = fields.Many2one('car.diagnoses')
    product_id = fields.Many2one('product.product')
    product_uom = fields.Many2one('uom.uom', string='Unit Of Measure')
    product_uom_qty = fields.Float(string="Quantity", default=1)

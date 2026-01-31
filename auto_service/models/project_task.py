# -*- coding: utf-8 -*-
""" Project Task """
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    """ Inherit Project Task """
    _inherit = 'project.task'

    car_diagnoses_id = fields.Many2one('car.diagnoses')
    reception_information_id = fields.Many2one('reception.information')
    task_location_id = fields.Many2one('task.location')
    task_finished = fields.Boolean()
    is_finished = fields.Boolean()
    service_name = fields.Char()
    estimated_time = fields.Float()
    check_pause_time = fields.Float()
    success_timer = fields.Float()
    s = fields.Boolean()
    task_status = fields.Selection(
        [('1', 'On Track'), ('2', 'Late')],
        default='1',
        string='Status',
        tracking=True
    )
    timer_check = fields.Datetime(default=fields.Datetime.now())
    spare_parts_task_ids = fields.One2many('spare.parts.task', 'project_task_id')
    timer_start = fields.Datetime(string='Timer Start')
    timer_pause = fields.Datetime(string='Timer Pause', default=False)

    def finish_task(self):
        """ Mark the task as finished """
        self.is_finished = True
        tasks = self.env['project.task'].search([
            ('project_id', '=', self.project_id.id)
        ])
        done = all(task.is_finished for task in tasks)
        if done:
            self.project_id.all_tasks_done = True

    def action_timer_start(self):
        """ Start the timer """
        if not self.timer_start:
            self.write({'timer_start': fields.Datetime.now()})

    def action_timer_resume(self):
        """ Resume the timer """
        if self.timer_pause:
            new_start = self.timer_start + (
                fields.Datetime.now() - self.timer_pause
            )
            self.write({'timer_start': new_start, 'timer_pause': False})
        else:
            raise UserError(_("The timer is not paused and cannot be resumed."))

    @api.model
    def create(self, vals):
        """ Override create() """
        res = super(ProjectTask, self).create(vals)
        res.action_timer_start()  # Start the timer
        if res.timer_pause:  # Resume the timer if paused
            res.action_timer_resume()
        if res.timer_start:
            m = int(res.timer_start.strftime("%M"))
            res.success_timer = m
        return res


class SparePartsTask(models.Model):
    """ Spare Parts Task """
    _name = 'spare.parts.task'
    _description = 'Spare Parts Task'

    project_task_id = fields.Many2one('project.task')
    product_id = fields.Many2one('product.product')
    unit_price = fields.Float()
    product_qty = fields.Float(string="Quantity", default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    subtotal = fields.Float()
    available_quantity = fields.Float()
    service_name = fields.Char()
    task = fields.Char()

""" Initialize Models """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import datetime


class StockPicking(models.Model):
    """
        Inherit Stock Picking:
         -
    """
    _inherit = 'stock.picking'

    timer_start = fields.Datetime("Timer Start")
    timer_stop = fields.Float()
    timer_pause = fields.Datetime("Timer Last Pause")
    is_timer_running = fields.Boolean(compute="_compute_is_timer_running")
    res_model = fields.Char()
    res_id = fields.Integer()
    user_id = fields.Many2one('res.users')
    stop_timer = fields.Boolean()
    start_timer = fields.Boolean()
    reception_ok = fields.Boolean()
    account_analytic_id = fields.Many2one('account.analytic.account')
    car_creations_id = fields.Many2one('car.creations', string="Chassis Number", tracking=True,
                                       related='sale_id.car_diagnoses_id.car_creations_id')
    license_plate_no = fields.Char(tracking=True, related='sale_id.car_diagnoses_id.license_plate_no')

    _sql_constraints = [(
        'unique_timer', 'UNIQUE(res_model, res_id, user_id)',
        'Only one timer occurrence by model, record and user')]

    def _compute_state(self):
        """ Override _compute_state """
        super(StockPicking, self)._compute_state()
        for rec in self:
            if rec.state == 'done':
                rec.action_timer_pause()

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
    def create(self, vals_list):
        """ Override create """
        # vals_list ={'field': value}  -> dectionary contains only new filled fields
        res = super(StockPicking, self).create(vals_list)
        res.action_timer_start()
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

    @api.model
    def get_server_time(self):
        """ Returns the server time.
            The timer widget needs the server time instead of the client time
            to avoid time desynchronization issues like the timer beginning at 0:00
            and not 23:59 and so on.
        """
        return fields.Datetime.now()

    @api.model
    def get_server_time(self):
        """ Returns the server time.
            The timer widget needs the server time instead of the client time
            to avoid time desynchronization issues like the timer beginning at 0:00
            and not 23:59 and so on.
        """
        return fields.Datetime.now()

    def view_action_auto_purchase_requisition(self):
        """ View Action auto_purchase_requisition """
        products = []
        for rec in self.move_ids_without_package:
            products.append((0, 0,
                             {'product_id': rec.product_id.id,
                              'uom_id': rec.product_uom.id,
                              'quantity': rec.product_uom_qty
                              }))
        action = \
            self.env.ref(
                'auto_service.auto_purchase_requisition_action').read()[
                0]
        action['views'] = [
            (self.env.ref('auto_service.auto_purchase_requisition_form').id,
             'form')]
        action['context'] = {'default_purchase_requisition_lines_ids': products}

        return action

    def action_assign(self):
        """ inherit action_assign() """
        res = super(StockPicking, self).action_assign()
        for p in self.move_ids_without_package:
            quantity = self.env['stock.quant'].search([
                ('product_id', '=', p.product_id.id),
                ('location_id.usage', '=', 'internal')
            ], limit=1)
            p.available_quantity = quantity.inventory_quantity_auto_apply
        return res

    def button_validate(self):
        self.reception_ok = True
        if self.state == 'done':
            self.action_timer_stop()
        return super(StockPicking, self).button_validate()

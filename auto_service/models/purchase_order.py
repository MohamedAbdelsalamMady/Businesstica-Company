# -*- coding: utf-8 -*-
""" Purchase Order """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class PurchaseOrder(models.Model):
    """ inherit Purchase Order """
    _inherit = 'purchase.order'

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
        res = super(PurchaseOrder, self).create(vals)
        res.action_timer_start()
        return res

    def button_confirm(self):
        """ inherit button_confirm() """
        super(PurchaseOrder, self).button_confirm()
        self.action_timer_pause()


# -*- coding: utf-8 -*-
""" Timer Mixin """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class TimerMixin(models.AbstractModel):
    """ Timer Mixin """
    _inherit = 'timer.mixin'

    # def _action_interrupt_user_timers(self):
    #     # Interruption is the action called when the timer is stoped by the start of another one
    #     self.action_timer_resume()
    #
    #
    def _stop_timer_in_progress(self):
        """
        Cancel the timer in progress if there is one
        Each model can interrupt the running timer in a specific way
        By setting it in pause or stop by example
        """
        timer = self._get_user_timers().filtered(lambda t: t.is_timer_running)
        if timer:
            model = self.env[timer.res_model].browse(timer.res_id)
            model._action_interrupt_user_timers()

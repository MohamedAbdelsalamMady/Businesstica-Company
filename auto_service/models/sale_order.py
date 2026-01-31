# -*- coding: utf-8 -*-
""" Sale Order """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class SaleOrder(models.Model):
    """ inherit Sale Order """
    _inherit = 'sale.order'

    car_diagnoses_id = fields.Many2one('car.diagnoses')
    from_car_diagnoses = fields.Boolean()
    reception_information_id = fields.Many2one('reception.information')
    car_creations_id = fields.Many2one('car.creations', string="Chassis Number")
    service_description = fields.Text()
    timer_start = fields.Datetime("Timer Start")
    timer_stop = fields.Float()

    def action_timer_start(self):
        if not self.timer_start:
            self.write({'timer_start': fields.Datetime.now()})

    @api.model
    def create(self, vals_list):
        """ Override create """
        res = super(SaleOrder, self).create(vals_list)
        res.action_timer_start()
        return res

    def action_timer_stop(self):
        """ Stop the timer and return the spent minutes since it started
            :return minutes_spent if the timer is started,
                    otherwise return False
        """
        if not self.timer_start:
            return False
        minutes_spent = self._get_minutes_spent()
        self.write({'timer_stop': minutes_spent, 'timer_start': False})
        return minutes_spent

    def _get_minutes_spent(self):
        start_time = self.timer_start
        stop_time = fields.Datetime.now()
        # timer was either running or paused
        return (stop_time - start_time).total_seconds() / 60

    def action_confirm(self):
        """ inherit action_confirm() """
        super(SaleOrder, self).action_confirm()
        self.car_diagnoses_id.sale_order_confirmed = True
        self.action_timer_stop()

    def _prepare_invoice(self):
        """ inherit _prepare_invoice() """
        res = super(SaleOrder, self)._prepare_invoice()
        res.update(car_diagnoses_id=self.car_diagnoses_id.id,
                   reception_information_id=self.reception_information_id.id,
                   car_creations_id=self.car_creations_id.id,
                   service_description=self.service_description,

                   )
        return res

    # @api.constrains('date_order')
    # def _check_date_order01(self):
    #     """ Validate date_order01 """
    #     if self.date_order<fields.Date.today():


class SaleOrderLine(models.Model):
    """ inherit Sale Order Line """
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res.update(available_quantity=self.product_id.qty_available)

        return res

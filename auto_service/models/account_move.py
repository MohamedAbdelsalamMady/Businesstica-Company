# -*- coding: utf-8 -*-
""" Account Move """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    """ inherit Account Move """
    _inherit = 'account.move'

    car_diagnoses_id = fields.Many2one('car.diagnoses')
    reception_information_id = fields.Many2one('reception.information')
    car_creations_id = fields.Many2one('car.creations',
                                       string="License Plate No")
    service_description = fields.Text()
    inspection_transfer_ownership_id = fields.Many2one('inspection.transfer.ownership')
    pre_travel_vehicle_inspection_id = fields.Many2one('pre.travel.vehicle.inspection')
    approved = fields.Boolean()
    drft_approve = fields.Boolean()
    notes = fields.Text()
    not_paid_allow_perm = fields.Boolean("Leave Permission", tracking=True)
    perm_user_id = fields.Many2one('res.users')

    @api.onchange('not_paid_allow_perm')
    def _assign_user(self):
        self.perm_user_id = self.env.user.id

    def button_draft(self):
        """ inherit button_draft() """
        super(AccountMove, self).button_draft()
        self.approved = False

    def button_cancel(self):
        """ inherit button_cancel() """
        super(AccountMove, self).button_cancel()
        self.drft_approve = False

    def action_post(self):
        """ inherit action_post() """
        super(AccountMove, self).action_post()
        self.reception_information_id.state = '6'

    def send_to_approve(self):
        """ Send To Approve """
        for rec in self:
            rec.approved = True

    def drft_to_approve(self):
        """ Send To Approve """
        for rec in self:
            rec.drft_approve = True

# -- coding: utf-8 --

##############################################################################
#                                                                            #
# Part of WebbyCrown Solutions (Website: www.webbycrown.com).                #
# Copyright © 2025 WebbyCrown Solutions. All Rights Reserved.                #
#                                                                            #
# This module is developed and maintained by WebbyCrown Solutions.           #
# Unauthorized copying of this file, via any medium, is strictly prohibited. #
# Licensed under the terms of the WebbyCrown Solutions License Agreement.    #
#                                                                            #
##############################################################################

from odoo import api, fields, models


class PharmacyControlledLog(models.Model):
    _name = 'pharmacy.controlled.log'
    _description = 'Controlled Drug Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _check_company_auto = True

    name = fields.Char(compute='_compute_name', store=True)
    hospital_id = fields.Many2one('hospital.hospital', required=True, index=True)
    pharmacy_id = fields.Many2one('pharmacy.pharmacy', domain="[('hospital_id','=',hospital_id)]", index=True)
    drug_id = fields.Many2one('pharmacy.drug', required=True, index=True)
    company_id = fields.Many2one(
        'res.company',
        related='hospital_id.company_id',
        store=True,
        readonly=True,
        index=True,
        help='Company that owns this controlled drug log entry. Derived from the hospital.',
    )
    qty = fields.Float(required=True)
    timestamp = fields.Datetime(default=fields.Datetime.now, index=True)
    action_type = fields.Selection([
        ('dispense', 'Dispense'), ('return', 'Return'), ('destroy', 'Destroy')
    ], required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    notes = fields.Text()

    @api.constrains('qty')
    def _check_qty_positive(self):
        """Ensure quantity is positive."""
        for rec in self:
            if rec.qty <= 0:
                raise models.ValidationError('Controlled drug quantity must be greater than zero.')

    @api.constrains('pharmacy_id', 'hospital_id')
    def _check_pharmacy_hospital(self):
        """Ensure pharmacy belongs to hospital if both are set."""
        for rec in self:
            if rec.pharmacy_id and rec.hospital_id:
                if rec.pharmacy_id.hospital_id != rec.hospital_id:
                    raise models.ValidationError('Pharmacy must belong to the specified hospital.')
    
    # Pivot view count field
    count_field = fields.Integer(string='Count', compute='_compute_count_field', store=True, default=1)
    
    def _compute_count_field(self):
        for rec in self:
            rec.count_field = 1

    @api.depends('action_type', 'drug_id', 'qty', 'timestamp')
    def _compute_name(self):
        for rec in self:
            action = dict(self._fields['action_type'].selection).get(rec.action_type, '')
            drug = rec.drug_id.name or ''
            qty = rec.qty or 0
            when = rec.timestamp and rec.timestamp.strftime('%Y-%m-%d %H:%M') or ''
            rec.name = f"{action}: {drug} x{qty} @ {when}".strip()



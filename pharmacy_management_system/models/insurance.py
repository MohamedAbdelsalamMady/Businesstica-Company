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


class PharmacyInsuranceClaim(models.Model):
    _name = 'pharmacy.insurance.claim'
    _description = 'Insurance Claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    hospital_id = fields.Many2one('hospital.hospital', required=True, default=lambda self: self.env.user.default_hospital_id, index=True)
    pharmacy_id = fields.Many2one('pharmacy.pharmacy', domain="[('hospital_id','=',hospital_id)]", index=True)
    name = fields.Char(required=True, default=lambda self: self.env['ir.sequence'].next_by_code('pharmacy.insurance.claim') or '/')
    prescription_id = fields.Many2one('pharmacy.prescription')
    patient_id = fields.Many2one('res.partner', domain="[('is_patient','=',True)]")
    insurance_company_id = fields.Many2one('res.partner')
    amount_claimed = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one(
        'res.company',
        related='hospital_id.company_id',
        store=True,
        readonly=True,
        index=True,
        help='Company that owns this insurance claim. Derived from the hospital.',
    )
    state = fields.Selection([
        ('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('paid', 'Paid'), ('rejected', 'Rejected')
    ], default='draft', tracking=True, index=True)

    @api.model
    def create(self, vals):
        """Auto-fill patient_id, hospital_id, pharmacy_id from prescription_id if not provided."""
        if vals.get('prescription_id') and not vals.get('patient_id'):
            prescription = self.env['pharmacy.prescription'].browse(vals['prescription_id'])
            if prescription.patient_id:
                vals['patient_id'] = prescription.patient_id.id
        if vals.get('prescription_id') and not vals.get('hospital_id'):
            prescription = self.env['pharmacy.prescription'].browse(vals['prescription_id'])
            if prescription.hospital_id:
                vals['hospital_id'] = prescription.hospital_id.id
        if vals.get('prescription_id') and not vals.get('pharmacy_id'):
            prescription = self.env['pharmacy.prescription'].browse(vals['prescription_id'])
            if prescription.pharmacy_id:
                vals['pharmacy_id'] = prescription.pharmacy_id.id
        return super().create(vals)

    @api.constrains('prescription_id', 'hospital_id', 'pharmacy_id')
    def _check_prescription_consistency(self):
        """Ensure hospital_id and pharmacy_id match the prescription if provided."""
        for rec in self:
            if rec.prescription_id:
                if rec.hospital_id and rec.prescription_id.hospital_id != rec.hospital_id:
                    raise models.ValidationError('Hospital must match the prescription\'s hospital.')
                if rec.pharmacy_id and rec.prescription_id.pharmacy_id and rec.prescription_id.pharmacy_id != rec.pharmacy_id:
                    raise models.ValidationError('Pharmacy must match the prescription\'s pharmacy.')
    
    # Pivot view count field
    count_field = fields.Integer(string='Count', compute='_compute_count_field', store=True, default=1)
    
    def _compute_count_field(self):
        for rec in self:
            rec.count_field = 1

    def action_submit(self):
        for rec in self:
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_paid(self):
        for rec in self:
            rec.state = 'paid'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'



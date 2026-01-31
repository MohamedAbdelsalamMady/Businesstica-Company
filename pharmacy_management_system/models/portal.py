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


class PharmacyPortalRequest(models.Model):
    _name = 'pharmacy.portal.request'
    _description = 'Pharmacy Portal Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'state, create_date desc'

    hospital_id = fields.Many2one('hospital.hospital', required=True)
    pharmacy_id = fields.Many2one('pharmacy.pharmacy', domain="[('hospital_id','=',hospital_id)]")
    name = fields.Char(required=True, default=lambda self: self.env['ir.sequence'].next_by_code('pharmacy.portal.request') or '/')
    partner_id = fields.Many2one('res.partner')
    type = fields.Selection([('upload', 'Upload'), ('reservation', 'Reservation'), ('query', 'Query')], default='upload')
    attachment_ids = fields.Many2many('ir.attachment')
    state = fields.Selection([('new', 'New'), ('processing', 'Processing'), ('done', 'Done')], default='new')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Clinical / classification flags
    is_doctor = fields.Boolean(
        help='Check this box if this contact is a doctor or prescriber who can issue prescriptions.',
    )
    is_patient = fields.Boolean(
        help='Check this box if this contact is a patient who can receive prescriptions and treatments.',
    )
    is_pharmacy_customer = fields.Boolean(
        string='Pharmacy Customer',
        help='Check this box if this contact is a pharmacy customer who can make purchases and use loyalty programs.',
    )

    # Core demographics
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    dob = fields.Date(string='Date of Birth')
    medical_record_no = fields.Char()
    
    # Pharmacy profile
    preferred_pharmacy_id = fields.Many2one('pharmacy.pharmacy', string='Preferred Pharmacy')
    loyalty_card = fields.Char(string='Loyalty Card')

    # Doctor / prescriber metadata
    license_number = fields.Char(
        string='License Number',
        help='Medical license number for this doctor/prescriber. Should be unique per doctor.',
    )
    specialty = fields.Char(string='Specialty')
    default_pharmacy_id = fields.Many2one('pharmacy.pharmacy', string='Default Pharmacy')
    
    @api.constrains('license_number', 'company_id')
    def _check_license_number_unique(self):
        """Ensure license number is unique per company when provided."""
        for rec in self:
            if rec.license_number and rec.is_doctor:
                domain = [
                    ('license_number', '=', rec.license_number),
                    ('id', '!=', rec.id),
                    ('is_doctor', '=', True),
                ]
                if rec.company_id:
                    domain.append(('company_id', '=', rec.company_id.id))
                if self.search(domain):
                    raise models.ValidationError('License number must be unique per company for doctors.')

    @api.constrains('medical_record_no', 'company_id')
    def _check_medical_record_no_unique(self):
        """Ensure medical record number is unique per company when provided."""
        for rec in self:
            if rec.medical_record_no and rec.is_patient:
                domain = [
                    ('medical_record_no', '=', rec.medical_record_no),
                    ('id', '!=', rec.id),
                    ('is_patient', '=', True),
                ]
                if rec.company_id:
                    domain.append(('company_id', '=', rec.company_id.id))
                if self.search(domain):
                    raise models.ValidationError('Medical record number must be unique per company for patients.')

    # Health-lite fields
    blood_type = fields.Selection(
        [
            ('a+', 'A+'),
            ('a-', 'A-'),
            ('b+', 'B+'),
            ('b-', 'B-'),
            ('ab+', 'AB+'),
            ('ab-', 'AB-'),
            ('o+', 'O+'),
            ('o-', 'O-'),
        ]
    )
    allergy_note = fields.Text()
    chronic_conditions = fields.Text()

    # Smart button / KPI counts
    prescription_count = fields.Integer(
        string='Prescriptions',
        compute='_compute_prescription_count',
        help='Total number of prescriptions issued to this patient.',
    )
    treatment_count = fields.Integer(
        string='Treatments',
        compute='_compute_treatment_count',
        help='Total number of treatment episodes for this patient.',
    )
    purchase_count = fields.Integer(
        string='Purchases',
        compute='_compute_purchase_count',
        help='Total number of purchase transactions for this customer.',
    )
    rx_count_total = fields.Integer(
        string='Total RX',
        compute='_compute_rx_counts',
        help='Total number of prescriptions written by this doctor.',
    )
    rx_count_by_pharmacy = fields.Integer(
        string='RX (Default Pharmacy)',
        compute='_compute_rx_counts',
        help='Number of prescriptions written by this doctor at their default pharmacy.',
    )
    
    @api.depends('is_patient')
    def _compute_prescription_count(self):
        """Optimized prescription count using read_group."""
        patient_ids = self.filtered('is_patient').ids
        if not patient_ids:
            for rec in self:
                rec.prescription_count = 0
            return
        
        Prescription = self.env['pharmacy.prescription']
        rx_data = Prescription.read_group(
            [('patient_id', 'in', patient_ids)],
            ['patient_id'],
            ['patient_id'],
        )
        rx_counts = {item['patient_id'][0]: item.get('__count', 0) for item in rx_data if item.get('patient_id')}
        
        for rec in self:
            if rec.is_patient:
                rec.prescription_count = rx_counts.get(rec.id, 0)
            else:
                rec.prescription_count = 0
    
    @api.depends('is_patient')
    def _compute_treatment_count(self):
        """Optimized treatment count using read_group."""
        patient_ids = self.filtered('is_patient').ids
        if not patient_ids:
            for rec in self:
                rec.treatment_count = 0
            return
        
        Treatment = self.env['hospital.treatment']
        treatment_data = Treatment.read_group(
            [('patient_id', 'in', patient_ids)],
            ['patient_id'],
            ['patient_id'],
        )
        treatment_counts = {item['patient_id'][0]: item.get('__count', 0) for item in treatment_data if item.get('patient_id')}
        
        for rec in self:
            if rec.is_patient:
                rec.treatment_count = treatment_counts.get(rec.id, 0)
            else:
                rec.treatment_count = 0

    @api.depends('is_doctor', 'default_pharmacy_id')
    def _compute_rx_counts(self):
        """Optimized RX counts for doctors using read_group."""
        doctor_ids = self.filtered('is_doctor').ids
        if not doctor_ids:
            for rec in self:
                rec.rx_count_total = 0
                rec.rx_count_by_pharmacy = 0
            return
        
        Prescription = self.env['pharmacy.prescription']
        # Batch total RX counts
        rx_data = Prescription.read_group(
            [('doctor_id', 'in', doctor_ids)],
            ['doctor_id'],
            ['doctor_id'],
        )
        rx_counts = {item['doctor_id'][0]: item.get('__count', 0) for item in rx_data if item.get('doctor_id')}
        
        # Batch pharmacy-specific RX counts
        doctors_with_pharmacy = self.filtered(lambda r: r.is_doctor and r.default_pharmacy_id)
        pharmacy_rx_counts = {}
        if doctors_with_pharmacy:
            pharmacy_rx_data = Prescription.read_group(
                [
                    ('doctor_id', 'in', doctors_with_pharmacy.ids),
                    ('pharmacy_id', 'in', doctors_with_pharmacy.mapped('default_pharmacy_id').ids),
                ],
                ['doctor_id', 'pharmacy_id'],
                ['doctor_id', 'pharmacy_id'],
            )
            for item in pharmacy_rx_data:
                if item.get('doctor_id') and item.get('pharmacy_id'):
                    doctor_id = item['doctor_id'][0]
                    pharmacy_id = item['pharmacy_id'][0]
                    doctor = self.browse(doctor_id)
                    if doctor.default_pharmacy_id.id == pharmacy_id:
                        pharmacy_rx_counts[doctor_id] = item.get('__count', 0)
        
        for rec in self:
            if rec.is_doctor:
                rec.rx_count_total = rx_counts.get(rec.id, 0)
                rec.rx_count_by_pharmacy = pharmacy_rx_counts.get(rec.id, 0)
            else:
                rec.rx_count_total = 0
                rec.rx_count_by_pharmacy = 0

    def _compute_purchase_count(self):
        """Placeholder until purchase/sales linkage is implemented."""
        for rec in self:
            rec.purchase_count = 0

    def action_view_prescriptions(self):
        """Open patient prescriptions"""
        self.ensure_one()
        if not self.is_patient:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'pharmacy.prescription',
            'domain': [('patient_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_doctor_prescriptions(self):
        """Open prescriptions where this partner is the doctor."""
        self.ensure_one()
        if not self.is_doctor:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Doctor Prescriptions',
            'res_model': 'pharmacy.prescription',
            'domain': [('doctor_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_treatments(self):
        """Open treatments for the patient"""
        self.ensure_one()
        if not self.is_patient:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Treatments',
            'res_model': 'hospital.treatment',
            'domain': [('patient_id', '=', self.id)],
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }


class PortalMessageConfig(models.Model):
    _name = 'portal.message.config'
    _description = 'Portal Message Configuration'
    _rec_name = 'name'

    name = fields.Char(required=True, help='Template name for identification.')
    channel = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('portal', 'Portal')
    ], required=True, help='Communication channel for this message template.')
    template_id = fields.Many2one(
        'mail.template',
        string='Mail Template',
        help='Email template reference for email channel messages.',
    )
    active = fields.Boolean(default=True, help='Whether this message configuration is active.')



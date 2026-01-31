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


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _description = "Hospital Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    # Identifiers & core demographics
    name = fields.Char(required=True, tracking=True)
    patient_code = fields.Char(readonly=True, copy=False, index=True, tracking=True)
    patient_type = fields.Selection(
        [
            ("adult", "Adult"),
            ("pediatric", "Pediatric"),
        ],
        default="adult",
        required=True,
        tracking=True,
    )
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        tracking=True,
    )
    birth_date = fields.Date(tracking=True)

    # Contact details
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()

    # Relations
    partner_id = fields.Many2one("res.partner", string="Contact")
    insurance_id = fields.Many2one("res.partner", string="Insurance Company")

    # Clinical metadata
    blood_type = fields.Selection(
        [
            ("a+", "A+"),
            ("a-", "A-"),
            ("b+", "B+"),
            ("b-", "B-"),
            ("ab+", "AB+"),
            ("ab-", "AB-"),
            ("o+", "O+"),
            ("o-", "O-"),
        ]
    )
    allergy_note = fields.Text()
    medical_history = fields.Text()

    # Emergency contact
    emergency_contact_name = fields.Char()
    emergency_contact_phone = fields.Char()

    active = fields.Boolean(default=True)

    # Admin / company fields
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Smart button counts
    appointment_count = fields.Integer(
        compute="_compute_appointment_count",
        help='Number of appointments for this patient. (Currently not implemented - appointment model removed)',
    )
    treatment_count = fields.Integer(
        compute="_compute_treatment_count",
        help='Number of treatment episodes for this patient.',
    )
    prescription_count = fields.Integer(
        compute="_compute_prescription_count",
        help='Number of prescriptions issued to this patient.',
    )
    invoice_count = fields.Integer(
        compute="_compute_invoice_count",
        help='Number of invoices for this patient. (Requires account module integration)',
    )

    _sql_constraints = [
        ("patient_code_uniq", "unique(patient_code, company_id)", "Patient code must be unique per company."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if not vals.get("patient_code"):
                vals["patient_code"] = seq.next_by_code("pharmacy_management_system.seq_patient") or "/"
        return super().create(vals_list)

    # Smart button computes
    def _compute_appointment_count(self):
        """Appointment count - placeholder since appointment model was removed."""
        for patient in self:
            patient.appointment_count = 0

    def _compute_treatment_count(self):
        """Optimized treatment count using read_group."""
        patient_ids = self.ids
        if not patient_ids:
            for patient in self:
                patient.treatment_count = 0
            return
        
        Treatment = self.env['hospital.treatment']
        # Match by partner_id if available, otherwise by name/email
        treatment_data = Treatment.read_group(
            [('patient_id', 'in', patient_ids)],
            ['patient_id'],
            ['patient_id'],
        )
        treatment_counts = {item['patient_id'][0]: item.get('__count', 0) for item in treatment_data if item.get('patient_id')}
        
        # Also check by partner_id if patient has partner_id
        patients_with_partner = self.filtered('partner_id')
        if patients_with_partner:
            partner_treatment_data = Treatment.read_group(
                [('patient_id', 'in', patients_with_partner.mapped('partner_id').ids)],
                ['patient_id'],
                ['patient_id'],
            )
            partner_treatment_counts = {item['patient_id'][0]: item.get('__count', 0) for item in partner_treatment_data if item.get('patient_id')}
            for patient in patients_with_partner:
                if patient.partner_id.id in partner_treatment_counts:
                    treatment_counts[patient.id] = treatment_counts.get(patient.id, 0) + partner_treatment_counts[patient.partner_id.id]
        
        for patient in self:
            patient.treatment_count = treatment_counts.get(patient.id, 0)

    def _compute_prescription_count(self):
        """Optimized prescription count using read_group."""
        patient_ids = self.ids
        if not patient_ids:
            for patient in self:
                patient.prescription_count = 0
            return
        
        Prescription = self.env['pharmacy.prescription']
        # Match by partner_id if available
        patients_with_partner = self.filtered('partner_id')
        prescription_counts = {}
        
        if patients_with_partner:
            partner_ids = patients_with_partner.mapped('partner_id').ids
            rx_data = Prescription.read_group(
                [('patient_id', 'in', partner_ids)],
                ['patient_id'],
                ['patient_id'],
            )
            partner_rx_counts = {item['patient_id'][0]: item.get('__count', 0) for item in rx_data if item.get('patient_id')}
            for patient in patients_with_partner:
                if patient.partner_id.id in partner_rx_counts:
                    prescription_counts[patient.id] = partner_rx_counts[patient.partner_id.id]
        
        for patient in self:
            patient.prescription_count = prescription_counts.get(patient.id, 0)

    def _compute_invoice_count(self):
        """Invoice count - placeholder for account module integration."""
        for patient in self:
            patient.invoice_count = 0



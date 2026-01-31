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


class HospitalHospital(models.Model):
    _name = 'hospital.hospital'
    _description = 'Hospital'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(required=True)
    code = fields.Char()
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        help='Company that owns this hospital. Used for multi-company isolation.',
    )
    partner_id = fields.Many2one('res.partner', string='Address/Contact')
    warehouse_id = fields.Many2one('stock.warehouse', string='Default Warehouse')
    pharmacy_ids = fields.One2many('pharmacy.pharmacy', 'hospital_id', string='Pharmacies')
    api_config_ids = fields.One2many('hospital.api.config', 'hospital_id', string='API Configs')
    active = fields.Boolean(default=True)
    
    # Smart button counts
    pharmacy_count = fields.Integer(string='Pharmacies', compute='_compute_pharmacy_count')
    prescription_count = fields.Integer(string='Prescriptions', compute='_compute_prescription_count')
    treatment_count = fields.Integer(string='Treatments', compute='_compute_treatment_count')
    
    @api.depends('pharmacy_ids')
    def _compute_pharmacy_count(self):
        for rec in self:
            rec.pharmacy_count = len(rec.pharmacy_ids)
    
    @api.depends('name')
    def _compute_prescription_count(self):
        """Optimized prescription count using read_group."""
        hospital_ids = self.ids
        if not hospital_ids:
            for rec in self:
                rec.prescription_count = 0
            return
        
        Prescription = self.env['pharmacy.prescription']
        rx_data = Prescription.read_group(
            [('hospital_id', 'in', hospital_ids)],
            ['hospital_id'],
            ['hospital_id'],
        )
        rx_counts = {item['hospital_id'][0]: item.get('__count', 0) for item in rx_data if item.get('hospital_id')}
        
        for rec in self:
            rec.prescription_count = rx_counts.get(rec.id, 0)

    @api.depends('name')
    def _compute_treatment_count(self):
        """Optimized treatment count using read_group."""
        hospital_ids = self.ids
        if not hospital_ids:
            for rec in self:
                rec.treatment_count = 0
            return
        
        Treatment = self.env['hospital.treatment']
        treatment_data = Treatment.read_group(
            [('hospital_id', 'in', hospital_ids)],
            ['hospital_id'],
            ['hospital_id'],
        )
        treatment_counts = {item['hospital_id'][0]: item.get('__count', 0) for item in treatment_data if item.get('hospital_id')}
        
        for rec in self:
            rec.treatment_count = treatment_counts.get(rec.id, 0)

    def action_view_pharmacies(self):
        """Open related pharmacies"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pharmacies',
            'res_model': 'pharmacy.pharmacy',
            'domain': [('hospital_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_prescriptions(self):
        """Open related prescriptions"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'pharmacy.prescription',
            'domain': [('hospital_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_treatments(self):
        """Open related treatments"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Treatments',
            'res_model': 'hospital.treatment',
            'domain': [('hospital_id', '=', self.id)],
            'view_mode': 'kanban,tree,form',
            'target': 'current',
            'context': {'default_hospital_id': self.id},
        }



class HospitalDepartment(models.Model):
    _name = 'hospital.department'
    _description = 'Hospital Department'

    name = fields.Char(required=True)
    hospital_id = fields.Many2one('hospital.hospital', required=True)
    code = fields.Char()
    manager_id = fields.Many2one('res.users', string='Manager')
    active = fields.Boolean(default=True)


class HospitalApiConfig(models.Model):
    _name = 'hospital.api.config'
    _description = 'Hospital API Configuration'

    name = fields.Char(required=True, default='FHIR/HL7 Endpoint')
    hospital_id = fields.Many2one('hospital.hospital', required=True)
    endpoint_url = fields.Char(
        required=True,
        help='Primary API endpoint URL (e.g., FHIR/HL7 server URL). Must be unique per hospital.',
    )
    branch_base_url = fields.Char(
        help='Base URL for branch-specific endpoints. This differs from endpoint_url which is the main API endpoint.',
    )
    auth_token = fields.Char()

    _sql_constraints = [
        ('endpoint_hospital_uniq', 'unique(endpoint_url, hospital_id)', 'Endpoint URL must be unique per hospital.'),
    ]
    enabled = fields.Boolean(default=False)
    last_sync = fields.Datetime()


class ResUsers(models.Model):
    _inherit = 'res.users'

    default_hospital_id = fields.Many2one('hospital.hospital', string='Default Hospital')
    hospital_access_ids = fields.Many2many('hospital.hospital', string='Hospitals Access')



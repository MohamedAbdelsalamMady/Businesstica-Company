# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PediatricPrescription(models.Model):
    _name = 'pediatric.prescription'
    _description = 'Prescription/Ordonnance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'prescription_date desc'

    name = fields.Char('Référence', default='Nouvelle ordonnance', readonly=True)
    patient_id = fields.Many2one('pediatric.patient', 'Patient', required=True, tracking=True)
    consultation_id = fields.Many2one('pediatric.consultation', 'Consultation')
    prescription_date = fields.Date('Date prescription', required=True, default=fields.Date.today, tracking=True)
    diagnosis = fields.Char('Diagnostic')
    
    medication_line_ids = fields.One2many('pediatric.prescription.line', 'prescription_id', 'Médicaments')
    recommendations = fields.Text('Recommandations générales')
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('prescribed', 'Prescrite'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True)
    
    patient_age = fields.Integer(string='Âge patient', compute='_compute_patient_info', store=True)
    patient_weight = fields.Float(string='Poids patient', compute='_compute_patient_info', store=True)

    @api.depends('patient_id', 'patient_id.age', 'patient_id.weight')
    def _compute_patient_info(self):
        for rec in self:
            if rec.patient_id:
                rec.patient_age = rec.patient_id.age
                rec.patient_weight = rec.patient_id.weight
            else:
                rec.patient_age = 0
                rec.patient_weight = 0.0

    medication_count = fields.Integer('Nombre médicaments', compute='_compute_medication_count')
    
    @api.depends('medication_line_ids')
    def _compute_medication_count(self):
        for prescription in self:
            prescription.medication_count = len(prescription.medication_line_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouvelle ordonnance') == 'Nouvelle ordonnance':
                vals['name'] = self.env['ir.sequence'].next_by_code('pediatric.prescription') or 'ORD-NEW'
        return super(PediatricPrescription, self).create(vals_list)

    def action_prescribe(self):
        self.state = 'prescribed'

    def action_print(self):
        try:
            return self.env.ref('pediatric_management.action_report_prescription').report_action(self)
        except Exception:
            return True

    def action_cancel(self):
        self.state = 'cancelled'

class PediatricPrescriptionLine(models.Model):
    _name = 'pediatric.prescription.line'
    _description = 'Ligne de prescription'

    prescription_id = fields.Many2one('pediatric.prescription', 'Prescription', required=True, ondelete='cascade')
    medication_id = fields.Many2one('pediatric.medication', 'Médicament', required=True)
    
    # --- LES CHAMPS ATTENDUS PAR LA VUE XML ---
    medication_form = fields.Char(string='Forme', compute='_compute_medication_details', store=True)
    medication_concentration = fields.Char(string='Concentration', compute='_compute_medication_details', store=True)
    
    dosage = fields.Char('Dosage')
    frequency = fields.Char('Fréquence')
    duration = fields.Char('Durée')
    qty_to_dispense = fields.Char('Quantité à délivrer')
    instructions = fields.Text('Instructions spéciales')
    calculated_dose = fields.Char('Dose calculée', compute='_compute_dose')
    
    @api.depends('medication_id')
    def _compute_medication_details(self):
        for line in self:
            if line.medication_id:
                # On récupère la concentration si elle existe, sinon vide
                line.medication_concentration = getattr(line.medication_id, 'concentration', '')
                
                # On récupère la forme (on gère le cas Selection ou Char)
                try:
                    m_field = line.medication_id._fields['form']
                    if hasattr(m_field, 'selection') and m_field.selection:
                        form_val = dict(m_field.selection).get(line.medication_id.form, line.medication_id.form)
                        line.medication_form = form_val
                    else:
                        line.medication_form = line.medication_id.form
                except Exception:
                    line.medication_form = getattr(line.medication_id, 'form', '')
            else:
                line.medication_concentration = False
                line.medication_form = False

    @api.depends('medication_id', 'prescription_id.patient_weight')
    def _compute_dose(self):
        for line in self:
            line.calculated_dose = ""
            if line.medication_id and line.prescription_id.patient_weight:
                dose_rate = getattr(line.medication_id, 'dose_per_kg', 0)
                if dose_rate:
                    total = line.prescription_id.patient_weight * dose_rate
                    line.calculated_dose = f"{total:.1f} (Dose: {dose_rate}/kg)"
                else:
                    line.calculated_dose = "Manuel"
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PediatricConsultation(models.Model):
    _name = 'pediatric.consultation'
    _description = 'Consultation Médicale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'consultation_date desc'

    # --- IDENTIFICATION ---
    name = fields.Char(string='Référence', readonly=True, copy=False, default='/')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    # --- RELATIONS ---
    patient_id = fields.Many2one('pediatric.patient', string='Patient', required=True, tracking=True)
    patient_age = fields.Char(related='patient_id.age_display', string='Âge', readonly=True)
    
    # --- INFOS CONSULTATION ---
    consultation_date = fields.Date(string='Date', default=fields.Date.today, required=True)
    consultation_type = fields.Selection([
        ('routine', 'Suivi de routine'),
        ('sick', 'Enfant malade'),
        ('vaccination', 'Vaccination'),
        ('emergency', 'Urgence'),
    ], string='Type de consultation', default='routine')
    
    reason = fields.Char(string='Motif', required=True)
    symptoms = fields.Text(string='Symptômes')
    diagnosis = fields.Text(string='Diagnostic / Observations')

    # --- PROCHAIN RENDEZ-VOUS (Correction finale) ---
    next_appointment_needed = fields.Boolean(string='RDV Contrôle nécessaire', default=False)
    next_appointment_date = fields.Date(string='Date du prochain RDV')
    next_appointment_type = fields.Selection([
        ('control', 'Contrôle'),
        ('vaccination', 'Vaccination'),
        ('specialist', 'Spécialiste'),
    ], string='Type de prochain RDV', default='control')
    
    # LE CHAMP QUI CAUSAIT L'ERREUR :
    next_appointment_notes = fields.Text(string='Notes pour le prochain RDV')

    # --- PARAMÈTRES VITAUX ---
    weight = fields.Float(string='Poids (kg)')
    height = fields.Float(string='Taille (cm)')
    temperature = fields.Float(string='Température (°C)', digits=(3, 1))
    blood_pressure = fields.Char(string='Tension Artérielle')
    bmi = fields.Float(string='IMC', compute='_compute_bmi', store=True)
    bmi_status = fields.Selection([
        ('under', 'Insuffisance'), ('normal', 'Normal'),
        ('over', 'Surpoids'), ('obese', 'Obésité')
    ], string='Statut IMC', compute='_compute_bmi', store=True)

    # --- LIENS DOCUMENTS ---
    appointment_id = fields.Many2one('calendar.event', string='Rendez-vous')
    prescription_id = fields.Many2one('pediatric.prescription', string='Ordonnance', readonly=True)
    invoice_id = fields.Many2one('account.move', string='Facture', readonly=True)

    # --- CALCUL IMC ---
    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for rec in self:
            if rec.weight and rec.height > 0:
                h = rec.height / 100
                rec.bmi = rec.weight / (h * h)
                if rec.bmi < 18.5: rec.bmi_status = 'under'
                elif rec.bmi < 25: rec.bmi_status = 'normal'
                elif rec.bmi < 30: rec.bmi_status = 'over'
                else: rec.bmi_status = 'obese'
            else:
                rec.bmi = 0
                rec.bmi_status = False

    # --- ACTIONS ---
    def action_done(self):
        self.write({'state': 'done'})

    def action_create_prescription(self):
        self.ensure_one()
        return {
            'name': _('Nouvelle Ordonnance'),
            'type': 'ir.actions.act_window',
            'res_model': 'pediatric.prescription',
            'view_mode': 'form',
            'context': {'default_patient_id': self.patient_id.id, 'default_consultation_id': self.id},
            'target': 'current',
        }

    def action_schedule_next_appointment(self):
        self.ensure_one()
        return {
            'name': _('Planifier RDV Contrôle'),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'context': {
                'default_name': _('Suivi : %s') % self.patient_id.name,
                'default_start': self.next_appointment_date,
                'default_description': self.next_appointment_notes,
            },
            'target': 'new',
        }

    def action_create_invoice(self):
        # Placeholder pour la facturation
        pass

    # --- CRUD ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('pediatric.consultation') or '/'
        return super().create(vals_list)
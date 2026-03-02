# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta

class PediatricAppointment(models.Model):
    _name = 'pediatric.appointment'
    _description = 'Rendez-vous'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc'
    _rec_name = 'name'

    name = fields.Char('Référence', default='Nouveau', readonly=True)
    patient_id = fields.Many2one('pediatric.patient', 'Patient', required=True, tracking=True)
    
    # --- SOLUTION DE SECOURS POUR ÉVITER L'ERREUR DE TYPE ---
    # On définit le champ en Integer manuellement sans 'related' direct
    patient_age = fields.Integer(string='Âge patient', compute='_compute_patient_age', store=True)

    @api.depends('patient_id', 'patient_id.age')
    def _compute_patient_age(self):
        for rec in self:
            rec.patient_age = rec.patient_id.age if rec.patient_id else 0
    # -------------------------------------------------------

    appointment_date = fields.Datetime('Date et heure', required=True, tracking=True, default=fields.Datetime.now)
    duration = fields.Float('Durée (heures)', default=0.5, tracking=True)
    end_datetime = fields.Datetime('Date de fin', compute='_compute_end_datetime', store=True)

    appointment_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('vaccination', 'Vaccination'),
        ('control', 'Contrôle'),
        ('emergency', 'Urgence')
    ], string='Type', default='consultation', required=True, tracking=True)
    
    state = fields.Selection([
        ('scheduled', 'Programmé'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('no_show', 'Absent')
    ], string='État', default='scheduled', tracking=True)
    
    notes = fields.Text('Notes')
    consultation_id = fields.Many2one('pediatric.consultation', 'Consultation associée')

    @api.depends('appointment_date', 'duration')
    def _compute_end_datetime(self):
        for rec in self:
            if rec.appointment_date and rec.duration:
                rec.end_datetime = rec.appointment_date + timedelta(minutes=rec.duration * 60)
            else:
                rec.end_datetime = rec.appointment_date

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('pediatric.appointment') or 'RDV-NEW'
        return super(PediatricAppointment, self).create(vals_list)

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'
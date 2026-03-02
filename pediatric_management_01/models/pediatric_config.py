# -*- coding: utf-8 -*-
from odoo import models, fields

class PediatricConfig(models.Model):
    _name = 'pediatric.config'
    _description = 'Configuration du Cabinet'

    name = fields.Char('Nom du Cabinet', required=True, default='Cabinet Pédiatrique')
    specialty = fields.Char('Spécialité', default='Pédiatrie')
    
    # Informations de contact (Ajouté pour corriger les erreurs XML)
    phone = fields.Char('Téléphone')
    email = fields.Char('Email')
    address = fields.Text('Adresse')
    logo = fields.Binary('Logo')
    
    # Textes pour les documents (Ordonnances/Rapports)
    header_text = fields.Text('En-tête des documents')
    footer_text = fields.Text('Pied de page des documents')
    
    # Tarification
    consultation_price = fields.Float('Prix Consultation', default=50.0)
    control_price = fields.Float('Prix Contrôle', default=40.0)
    vaccination_price = fields.Float('Prix Vaccination', default=25.0)
    emergency_price = fields.Float('Prix Urgence', default=80.0)
    
    # Planning
    default_appointment_duration = fields.Integer('Durée RDV (min)', default=30)
    lunch_break_start = fields.Char('Début Pause', default='12:00')
    lunch_break_end = fields.Char('Fin Pause', default='14:00')
    
    # Notifications
    reminder_enabled = fields.Boolean('Rappels activés', default=True)
    email_notifications = fields.Boolean('Email activé', default=True)
    sms_notifications = fields.Boolean('SMS activé', default=False)
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class PediatricGrowthChart(models.Model):
    _name = 'pediatric.growth.chart'
    _description = 'Courbe de croissance'
    _order = 'measurement_date desc'

    patient_id = fields.Many2one('pediatric.patient', 'Patient', required=True, ondelete='cascade')
    measurement_date = fields.Date('Date mesure', required=True, default=fields.Date.today)
    
    # Automatisation : l'âge en mois sera calculé par rapport à la date de naissance
    age_months = fields.Integer('Âge (mois)', compute='_compute_age_months', store=True)
    
    weight = fields.Float('Poids (kg)')
    height = fields.Float('Taille (cm)')
    head_circumference = fields.Float('Périmètre crânien (cm)')
    bmi = fields.Float('IMC', compute='_compute_bmi', store=True)
    
    percentile_weight = fields.Float('Percentile poids')
    percentile_height = fields.Float('Percentile taille')

    # Sécurité : Empêcher les valeurs négatives au niveau de la base de données
    _sql_constraints = [
        ('check_weight_pos', 'CHECK(weight >= 0)', 'Le poids doit être positif !'),
        ('check_height_pos', 'CHECK(height >= 0)', 'La taille doit être positive !'),
    ]

    @api.depends('measurement_date', 'patient_id.date_of_birth')
    def _compute_age_months(self):
        """ Calcule automatiquement l'âge en mois au moment de la mesure """
        for record in self:
            if record.patient_id.date_of_birth and record.measurement_date:
                dob = record.patient_id.date_of_birth
                md = record.measurement_date
                # Calcul de la différence en mois
                record.age_months = (md.year - dob.year) * 12 + md.month - dob.month
            else:
                record.age_months = 0

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.weight and record.height > 0:
                height_m = record.height / 100
                record.bmi = record.weight / (height_m * height_m)
            else:
                record.bmi = 0

    @api.model_create_multi
    def create(self, vals_list):
        """ Met à jour la fiche patient avec la dernière mesure prise """
        records = super().create(vals_list)
        for rec in records:
            if rec.weight or rec.height:
                rec.patient_id.write({
                    'weight': rec.weight or rec.patient_id.weight,
                    'height': rec.height or rec.patient_id.height,
                })
        return records
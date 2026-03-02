from odoo import models, fields

class PediatricMedication(models.Model):
    _name = 'pediatric.medication'
    _description = 'Base de données médicaments'
    _order = 'name'

    name = fields.Char('Nom commercial', required=True)
    active_substance = fields.Char('Principe actif')
    form = fields.Selection([
        ('syrup', 'Sirop'),
        ('tablet', 'Comprimé'),
        ('capsule', 'Gélule'),
        ('drops', 'Gouttes'),
        ('spray', 'Spray'),
        ('cream', 'Crème'),
        ('suppository', 'Suppositoire'),
	('powder', 'Poudre/Sachet'),
    ], string='Forme')
    concentration = fields.Char('Concentration')
    pediatric_dosage = fields.Text('Posologie pédiatrique')
    min_age_months = fields.Integer('Âge minimum (mois)')
    max_age_months = fields.Integer('Âge maximum (mois)')
    dose_per_kg = fields.Float('Dose par kg')
    contraindications = fields.Text('Contre-indications')
    active = fields.Boolean('Actif', default=True)
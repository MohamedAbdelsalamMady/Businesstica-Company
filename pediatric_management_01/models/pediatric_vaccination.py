from odoo import models, fields, api, _

class PediatricVaccination(models.Model):
    _name = 'pediatric.vaccination'
    _description = 'Vaccination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc'

    patient_id = fields.Many2one('pediatric.patient', 'Patient', required=True, tracking=True)
    vaccine_id = fields.Many2one('pediatric.vaccine', 'Vaccin', required=True, tracking=True)
    scheduled_date = fields.Date('Date prévue', required=True, tracking=True)
    actual_date = fields.Date('Date d\'administration', tracking=True)
    lot_number = fields.Char('Numéro de lot')
    notes = fields.Text('Notes')
    
    state = fields.Selection([
        ('scheduled', 'Programmé'),
        ('completed', 'Administré'),
        ('cancelled', 'Annulé')
    ], string='État', default='scheduled', tracking=True)

    def action_complete(self):
        for rec in self:
            rec.write({
                'state': 'completed',
                'actual_date': fields.Date.today()
            })

class PediatricVaccine(models.Model):
    _name = 'pediatric.vaccine'
    _description = 'Vaccin'

    name = fields.Char('Nom du vaccin', required=True)
    disease = fields.Char('Maladie')
    age_months = fields.Integer('Âge recommandé (mois)')
    doses_required = fields.Integer('Nombre de doses')
    interval_months = fields.Integer('Intervalle entre doses (mois)')
    mandatory = fields.Boolean('Obligatoire')
    active = fields.Boolean('Actif', default=True)
from odoo import models, fields

class Medicine(models.Model):
    _name = 'vet.medicine'
    _description = 'Medicine'

    name = fields.Char(string='Medicine Name', required=True)
    description = fields.Text(string='Description')

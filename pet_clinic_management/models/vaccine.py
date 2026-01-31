from odoo import models, fields

class Vaccine(models.Model):
    _name = 'vet.vaccine'
    _description = 'Vaccine List'

    name = fields.Char(string='Vaccine Name', required=True)
    description = fields.Text(string='Description')
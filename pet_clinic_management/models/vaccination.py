from odoo import models, fields

class Vaccination(models.Model):
    _name = 'vet.vaccination'
    _description = 'Pet Vaccination Record'

    pet_id = fields.Many2one('vet.pet', string='Pet', required=True)
    breed = fields.Char(related='pet_id.breed', string='Breed', store=True)
    age = fields.Integer(related='pet_id.age', string='Age', store=True)
    vaccine_id = fields.Many2one('vet.vaccine', string='Vaccine', required=True)
    vaccination_date = fields.Date(string='Date', required=True)
    next_due_date = fields.Date(string='Next Due Date')
    notes = fields.Text(string='Notes')

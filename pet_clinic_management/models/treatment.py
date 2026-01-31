from odoo import models, fields

class Treatment(models.Model):
    _name = 'vet.treatment'
    _description = 'Pet Treatment'

    appointment_id = fields.Many2one('vet.appointment', string='Related Appointment')
    pet_id = fields.Many2one(related='appointment_id.pet_id', string='Pet', store=True, readonly=False)
    breed = fields.Char(related='appointment_id.breed', string='Breed', store=True)
    age = fields.Integer(related='appointment_id.age', string='Age', store=True)
    treatment_date = fields.Date(string='Date', default=fields.Date.today)
    description = fields.Text(string='Treatment Description')
    veterinarian = fields.Many2one('res.users', string='Veterinarian')

from odoo import models, fields

class Pet(models.Model):
    _name = 'vet.pet'
    _description = 'Pet'

    name = fields.Char(string='Pet Name', required=True)
    pet_type = fields.Selection([
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('bird', 'Bird'),
        ('other', 'Other')
    ], string='Type', required=True)
    breed = fields.Char(string='Breed')
    age = fields.Integer(string='Age')
    owner_id = fields.Many2one('res.partner', string='Owner')
    notes = fields.Text(string='Notes')

    image = fields.Image(string='Image', max_width=128, max_height=128)

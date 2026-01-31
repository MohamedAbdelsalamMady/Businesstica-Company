from odoo import models, fields, api
import random
import string
from datetime import datetime

class Appointment(models.Model):
    _name = 'vet.appointment'
    _description = 'Pet Appointment'

    name = fields.Char(string='Appointment ID', required=True, copy=False, readonly=True, default='New')
    pet_id = fields.Many2one('vet.pet', string='Pet', required=True)
    owner_id = fields.Many2one(related='pet_id.owner_id', string='Owner', store=True)
    breed = fields.Char(related='pet_id.breed', string='Breed', store=True)
    age = fields.Integer(related='pet_id.age', string='Age', store=True)
    date = fields.Datetime(string='Appointment Date', required=True)
    reason = fields.Text(string='Reason for Visit')
    diagnosis = fields.Text(string='Diagnosis')
    # treatment = fields.Text(string='Treatment')


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            today = datetime.today()
            month = today.strftime("%m")       # e.g. "08"
            year = today.strftime("%y")        # e.g. "26"
            day = today.strftime("%d")         # e.g. "07"
            rand_str = ''.join(random.choices(string.ascii_uppercase, k=2))  # e.g. "IM"
            vals['name'] = f"PET{month}{year}{rand_str}{day}"
        return super().create(vals)

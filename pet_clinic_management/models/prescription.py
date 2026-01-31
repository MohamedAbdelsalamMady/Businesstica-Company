from odoo import models, fields, api

class Prescription(models.Model):
    _name = 'vet.prescription'
    _description = 'Pet Prescription'

    appointment_id = fields.Many2one('vet.appointment', string='Appointment', required=True)
    pet_id = fields.Many2one(related='appointment_id.pet_id', string='Pet', store=True)
    breed = fields.Char(related='appointment_id.breed', string='Breed', store=True)
    age = fields.Integer(related='appointment_id.age', string='Age', store=True)
    instructions = fields.Text(string='General Instructions')
    line_ids = fields.One2many('vet.prescription.line', 'prescription_id', string='Medicines')

    medicine_list = fields.Char(string="Medicines", compute='_compute_medicine_list')

    @api.depends('line_ids.medicine_id')
    def _compute_medicine_list(self):
        for rec in self:
            rec.medicine_list = ', '.join(rec.line_ids.mapped('medicine_id.name'))

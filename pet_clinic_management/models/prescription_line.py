from odoo import models, fields

class PrescriptionLine(models.Model):
    _name = 'vet.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one('vet.prescription', string='Prescription', required=True, ondelete='cascade')
    medicine_id = fields.Many2one('vet.medicine', string='Medicine', required=True)
    dosage = fields.Selection([
        ('1-0-0', 'Morning Only'),
        ('0-1-0', 'Afternoon Only'),
        ('0-0-1', 'Night Only'),
        ('1-1-1', 'Thrice a day')
    ], string="Dosage")
    instructions = fields.Text(string='Instructions')
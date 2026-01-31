# -*- coding: utf-8 -*-
""" New Diagnoses Items Wizard """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class NewDiagnosesItemsWizard(models.TransientModel):
    """ New Diagnoses Items Wizard """
    _name = 'new.diagnoses.items.wizard'
    _description = 'New Diagnoses Items Wizard'

    new_diagnoses_items_wizard_ids = fields.One2many('new.diagnoses.wizard.lines', 'new_diagnoses_items_wizard_id')

    def confirm(self):
        """ Confirm """
        active_id = self._context.get('active_id')
        diagnoses_id = self.env['car.diagnoses'].browse(active_id)
        product_service = []
        products = []
        for spr in self.new_diagnoses_items_wizard_ids:
            products.append((0, 0,
                             {'product_id': spr.product_id.id,
                              'product_uom': spr.product_uom.id,
                              'product_uom_qty': spr.product_uom_qty,

                              }))
            if spr.product_id.type== 'service':
                self.env['project.task'].create({'name': spr.product_id.name,
                                                 'car_diagnoses_id': diagnoses_id.id,
                                                 'partner_id': diagnoses_id.partner_id.id,
                                                 'project_id': diagnoses_id.project_id.id,
                                                 'reception_information_id': diagnoses_id.reception_information_id.id,
                                                 'service_name': diagnoses_id.service_description,
                                                 'estimated_time': diagnoses_id.estimated_time,
                                                 })

        sale_id = self.env['sale.order'].create(
            {'car_diagnoses_id': diagnoses_id.id,
             'reception_information_id': diagnoses_id.reception_information_id.id,
             'partner_id': diagnoses_id.partner_id.id,
             'from_car_diagnoses': True,
             'car_creations_id': diagnoses_id.car_creations_id.id,
             'service_description': diagnoses_id.service_description,
             'order_line': products})

        diagnoses_id.write({'new_diagnoses_items_ids': products})


class NewDiagnosesWizardLines(models.TransientModel):
    """ New Diagnoses Wizard Lines """
    _name = 'new.diagnoses.wizard.lines'
    _description = 'New Diagnoses Wizard Lines'

    new_diagnoses_items_wizard_id = fields.Many2one('new.diagnoses.items.wizard')
    product_id = fields.Many2one('product.product')
    product_uom = fields.Many2one('uom.uom', string='Unit Of Measure')
    product_uom_qty = fields.Float(string="Quantity", default=1)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ product_id """
        self.product_uom = self.product_id.uom_id.id
        self.product_uom_qty = 1

# -*- coding: utf-8 -*-
""" Send To Pricing """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class SendToPricing(models.TransientModel):
    """ Send To Pricing """
    _name = 'send.to.pricing'
    _description = 'Send To Pricing'

    send_to_pricing_line_ids = fields.One2many('send.to.pricing.line',
                                               'send_to_pricing_id')


    def create_pricing(self):
        """ Create Pricing """
        active_id = self._context.get('active_id')
        field_study_id = self.env['car.diagnoses'].browse(active_id)
        products = []
        for rec in self.send_to_pricing_line_ids:
            if rec.product_id and rec.sending_done:
                products.append((0, 0,
                                 {'product_id': rec.product_id.id,
                                  'uom_id': rec.uom_id.id,
                                  'qty_ordered': rec.planned_quantity,
                                  'initial_unit_price': rec.unit_cost_price,
                                  'spare_parts_diagnoses_id': rec.spare_parts_diagnoses_id.id
                                  }))

        self.env['pricing'].create(
            {'car_diagnoses_id': field_study_id.id,
             'reception_information_id':field_study_id.reception_information_id.id,
             'user_id': self.env.user.id,
             'initial_products_ids': products
             })
        items = self.env['pricing'].search(
            [('car_diagnoses_id', '=',
              field_study_id.id)])
        field_study_id.pricing_count = len(items.ids)


class SendToPricingLine(models.TransientModel):
    """ Send To Pricing Line """
    _name = 'send.to.pricing.line'
    _description = 'Send To Pricing Line'

    send_to_pricing_id = fields.Many2one('send.to.pricing')
    product_id = fields.Many2one('product.product',
                                 domain="[('id', '=', product_id)]")
    car_diagnoses_id = fields.Many2one('car.diagnoses')
    uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    planned_quantity = fields.Float()
    unit_cost_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    spare_parts_diagnoses_id = fields.Many2one('spare.parts.diagnoses')
    sending_done = fields.Boolean()

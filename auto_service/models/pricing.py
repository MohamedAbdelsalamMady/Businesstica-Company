# -*- coding: utf-8 -*-
""" Pricing """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class Pricing(models.Model):
    """ Pricing """
    _name = 'pricing'
    _description = 'Pricing'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        [('draft', 'Draft'), ('pricing_done', 'Pricing Done')],
        default='draft',tracking=True)
    name = fields.Char(string='Reference', required=True, copy=False,
                       default='New', readonly=True,tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Purchase Representative',
        default=lambda self: self.env.user,tracking=True)
    date_end = fields.Datetime(string='Pricing Deadline',tracking=True)
    reception_information_id = fields.Many2one('reception.information',tracking=True)
    initial_products_ids = fields.One2many('initial.products', 'pricing_id',tracking=True)
    pricing_orders_ids = fields.One2many('pricing.orders', 'pricing_id',tracking=True)
    lines_confirm_pricing_ids = fields.One2many('lines.confirm.pricing',
                                                'pricing_id',tracking=True)
    car_diagnoses_id = fields.Many2one('car.diagnoses',tracking=True)
    count_pricing_orders = fields.Integer(
        compute='_compute_count_pricing_orders', store=True,tracking=True)

    @api.model
    def create(self, vals):
        """ Override create method to sequence name """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'pricing') or '/'
        return super(Pricing, self).create(vals)

    def create_pricing_orders(self):
        """ Create Pricing orders"""
        products = []
        for rec in self.initial_products_ids:
            if rec.product_id:
                products.append((0, 0,
                                 {'product_id': rec.product_id.id,
                                  'name': rec.product_id.name,
                                  'uom_id': rec.uom_id.id,
                                  'product_qty': rec.qty_ordered,
                                  'price_unit': rec.initial_unit_price,
                                  'price_subtotal': rec.initial_unit_price * rec.qty_ordered,
                                  'spare_parts_diagnoses_id': rec.spare_parts_diagnoses_id.id
                                  }))

        self.env['pricing.orders'].create(
            {
                'pricing_id': self.id,
                'pricing_order_lines_ids': products
            })

    @api.depends('pricing_orders_ids')
    def _compute_count_pricing_orders(self):
        """ Compute count_pricing_orders value """
        for rec in self:
            rec.count_pricing_orders = len(rec.pricing_orders_ids.ids)

    def action_view_pricing_orders(self):
        """ Smart button to run action """
        products = []
        for rec in self.initial_products_ids:
            if rec.product_id:
                products.append((0, 0,
                                 {'product_id': rec.product_id.id,
                                  'name': rec.product_id.name,
                                  'uom_id': rec.uom_id.id,
                                  'product_qty': rec.qty_ordered,
                                  'price_unit': rec.initial_unit_price,
                                  'spare_parts_diagnoses_id': rec.spare_parts_diagnoses_id.id
                                  }))
        recs = self.mapped('pricing_orders_ids')
        action = self.env.ref('auto_service.pricing_orders_action').sudo().read()[
            0]
        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]
            action['context'] = {'default_pricing_id': self.id,
                                 'default_pricing_order_lines_ids': products}
        elif len(recs) == 1:
            action['views'] = [(self.env.ref(
                'auto_service.pricing_orders_form').id, 'form')]
            action['res_id'] = recs.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class InitialProducts(models.Model):
    """ Initial Products """
    _name = 'initial.products'
    _description = 'Initial Products'

    pricing_id = fields.Many2one('pricing')
    product_id = fields.Many2one('product.product')
    uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    qty_ordered = fields.Float(string='Ordered Quantities')
    initial_unit_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    spare_parts_diagnoses_id = fields.Many2one('spare.parts.diagnoses')


class PricingOrders(models.Model):
    """ Pricing Orders """
    _name = 'pricing.orders'
    _description = 'Pricing Orders'

    pricing_id = fields.Many2one('pricing')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
                             default='draft')
    pricing_orders_id = fields.Many2one('pricing.orders')
    name = fields.Char(string='Reference', required=True, copy=False,
                       default='New', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Vendor')
    partner_ref = fields.Char(string="Vendor Reference")
    date_end = fields.Datetime(string='Order Deadline')
    delivery_days = fields.Char()
    subtotal = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    note = fields.Text()
    pricing_order_lines_ids = fields.One2many('pricing.order.lines',
                                              'pricing_orders_id')
    amount_untaxed = fields.Monetary(currency_field='currency_id',
                                     compute='_compute_amount_all', store=True)
    amount_tax = fields.Monetary(currency_field='currency_id',
                                 compute='_compute_amount_all', store=True)
    totals = fields.Monetary(currency_field='currency_id',
                             compute='_compute_amount_all', store=True)

    def button_confirm(self):
        """ Button Confirm """
        for rec in self:
            rec.pricing_id.write(
                {'lines_confirm_pricing_ids': [(0, 0,
                                                {
                                                    'pricing_id': rec.pricing_id.id,
                                                    'pricing_orders_id': rec.id,
                                                    'partner_id': rec.partner_id.id,
                                                    'delivery_days': rec.delivery_days,
                                                    'note': rec.note,
                                                    'subtotal': rec.totals})]})
            rec.state = 'confirm'

    @api.model
    def create(self, vals):
        """ Override create method to sequence name """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'pricing.orders') or '/'
        return super(PricingOrders, self).create(vals)

    # @api.depends('pricing_order_lines_ids')
    # def _compute_totals(self):
    #     """ Compute totals value """
    #     for rec in self:
    #         totals = 0
    #         for pr in rec.pricing_order_lines_ids:
    #             totals += pr.price_subtotal
    #         rec.update({'totals': totals})

    @api.depends('pricing_order_lines_ids.price_subtotal',
                 'pricing_order_lines_ids.price_unit',
                 'pricing_order_lines_ids.tax_ids')
    def _compute_amount_all(self):
        """ Compute amount_all value """
        for order in self:
            amount_untaxed = amount_tax = 0.0

            for line in order.pricing_order_lines_ids:
                amount_untaxed += line.price_subtotal
                for tax in line.tax_ids:
                    amount_tax += (
                                          tax.amount * line.price_unit * line.product_qty) / 100

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'totals': amount_untaxed + amount_tax

            })


class PricingOrderLines(models.Model):
    """ Pricing Order Lines """
    _name = 'pricing.order.lines'
    _description = 'Pricing Order Lines'

    pricing_orders_id = fields.Many2one('pricing.orders')
    name = fields.Text(string='Description')
    product_qty = fields.Float(string='Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    product_id = fields.Many2one('product.product')
    price_unit = fields.Float(string='Unit Price', required=True,
                              digits='Product Price')
    tax_ids = fields.Many2many('account.tax',domain=[('type_tax_use', '=', 'purchase')])
    price_subtotal = fields.Monetary(string='Subtotal',
                                     currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    spare_parts_diagnoses_id = fields.Many2one('spare.parts.diagnoses')

    @api.onchange('product_id', 'price_unit', 'product_qty')
    def _onchange_subtotal(self):
        """ product_id """
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.product_qty


class LinesConfirmPricing(models.Model):
    """ Lines Confirm Pricing """
    _name = 'lines.confirm.pricing'
    _description = 'Lines Confirm Pricing'

    pricing_id = fields.Many2one('pricing')
    pricing_orders_id = fields.Many2one('pricing.orders')
    partner_id = fields.Many2one(
        'res.partner', string='Vendor')
    delivery_days = fields.Char()
    note = fields.Text()
    subtotal = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             default='draft')

    def button_done_pricing(self):
        """ Button Function """
        for rec in self.pricing_orders_id.pricing_order_lines_ids:
            price_done = self.env['spare.parts.diagnoses'].search(
                [('id', '=', rec.spare_parts_diagnoses_id.id)], limit=1)
            price_done.unit_price = rec.price_unit
            price_done.subtotal = rec.price_unit*price_done.product_qty
            self.pricing_id.state = 'pricing_done'
        for d in self.pricing_id.lines_confirm_pricing_ids:
            d.state = 'done'

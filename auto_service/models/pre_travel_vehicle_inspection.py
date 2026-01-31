# -*- coding: utf-8 -*-
""" Pre Travel Vehicle Inspection """
from odoo import api, fields, models, _
from odoo.exceptions import UserError,  ValidationError


class PreTravelVehicleInspection(models.Model):
    """ Pre Travel Vehicle Inspection """
    _name = 'pre.travel.vehicle.inspection'
    _description = 'Pre Travel Vehicle Inspection'


    name = fields.Char(default='NEW')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),('invoiced', 'Invoiced')],
        default='draft',
        string='Status'
    )
    account_move_ids = fields.One2many('account.move', 'pre_travel_vehicle_inspection_id')
    count_invoices = fields.Integer(compute='_compute_count_invoices', store=True)
    partner_id = fields.Many2one('res.partner',string="Customer")
    repair_order_number= fields.Char()
    chassis_no = fields.Many2one('car.creations',
                                 string="Chassis Number", tracking=True)
    plate_number = fields.Char()
    date = fields.Date(default=fields.Date.today())
    person_conducting_disclosure = fields.Char(string="The name of the person conducting the general disclosure")
    original_engine_number = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    engine_sound = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])

    engine_oil = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    transmission_oil = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    power_oil = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    brake_fluid = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    freezing_liquid = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    thongs = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    belts_car = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_drums = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    back_drums = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_staple = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    posterior_tail = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_shears = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    background_shears = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    steering_wheel_box = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    steering_wheel_bars = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])


    background_helpers = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    shakman = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    engine_bases = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    transmission_base = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    corona_sound = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    oil_leaks = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    tires = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    conditioning_hot = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    conditioning_cold = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    radio = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    interior_lighting = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    steering_wheel_case = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    case_steering_buttons = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="case of steering wheel buttons")
    front_seat_movements = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    read_odometer = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    test_result_device = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="Engine condition Test result with the device")
    airbag_system = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    transmission_system = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    rest_systems_car = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="The rest of the systems in the car")
    headlights = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    lanterns_background = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    front_glass = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    background_glass = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    movable_roof = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    side_mirrors = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    march_sound = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    charging_dynamo = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    battery_status = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    centerlock = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')])
    wiper_sprinklers = fields.Selection([('1', 'Valid'),('2', 'Not Valid'),('3','Needs Repair'),('4','Needs Change'),('5','Not Checked')],string="Wipers and wiper sprinklers")
    note = fields.Text()
    product_ids = fields.Many2many('product.product')
    reception_information_id = fields.Many2one('reception.information')


    @api.model
    def create(self, vals):
        """ Override create method to sequence name """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pre.travel.vehicle.inspection') or '/'
        return super(PreTravelVehicleInspection, self).create(vals)

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        result['product_ids'] = [(4, self.env.ref('auto_service.product_pre_travel_vehicle_inspection').id)]
        return result


    @api.depends('account_move_ids')
    def _compute_count_invoices(self):
        """ Compute  value """
        for rec in self:
            rec.count_invoices = len(rec.account_move_ids.ids)

    def action_travel_vehicle_inspection(self):
        """ Smart button to run action """
        recs = self.mapped('account_move_ids')

        action = \
            self.env.ref(
                'account.action_move_out_invoice_type').sudo().read()[
                0]

        if len(recs) > 1:
            action['domain'] = [('id', 'in', recs.ids)]

        elif len(recs) == 1:
            action['views'] = [
                (
                    self.env.ref('account.view_move_form').id,
                    'form')]
            action['res_id'] = recs.ids[0]
        else:
            action['views'] = [
                (
                    self.env.ref('account.view_move_form').id,
                    'form')]

        return action

    def confirm(self):
        """ Confirm """
        self.state='confirm'


    def create_invoice(self):
        """ Create Invoice """
        products=[]
        if self.product_ids:
            for rec in self.product_ids:
                products.append((0, 0,
                                 {
                                     'product_id': rec.id,
                                     'product_uom_id': rec.uom_id.id,

                                     'price_unit':rec.lst_price

                                 }))
            self.env['account.move'].create({'partner_id':self.partner_id.id,'reception_information_id':self.reception_information_id.id,'move_type':'out_invoice','invoice_line_ids':products,'pre_travel_vehicle_inspection_id':self.id})
            self.state='invoiced'
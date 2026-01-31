# -- coding: utf-8 --

##############################################################################
#                                                                            #
# Part of WebbyCrown Solutions (Website: www.webbycrown.com).                #
# Copyright © 2025 WebbyCrown Solutions. All Rights Reserved.                #
#                                                                            #
# This module is developed and maintained by WebbyCrown Solutions.           #
# Unauthorized copying of this file, via any medium, is strictly prohibited. #
# Licensed under the terms of the WebbyCrown Solutions License Agreement.    #
#                                                                            #
##############################################################################

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PharmacyPharmacy(models.Model):
    _name = 'pharmacy.pharmacy'
    _description = 'Pharmacy Branch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    hospital_id = fields.Many2one('hospital.hospital')
    name = fields.Char(required=True)
    code = fields.Char(
        help='Unique code for this pharmacy branch within the company. Used for identification and reporting.'
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        help='Main warehouse used to source stock for this pharmacy. If set, the location will be auto-derived from the warehouse.',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        help='Company that owns this pharmacy branch. Used for multi-company isolation.',
    )
    address_id = fields.Many2one('res.partner', string='Address')
    location_id = fields.Many2one(
        'stock.location',
        help='Primary stock location for this pharmacy. If not set, it will be auto-derived from the warehouse when a warehouse is selected.',
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        help='Default pricelist used for sales and pricing at this pharmacy branch.',
    )
    parent_pharmacy_id = fields.Many2one('pharmacy.pharmacy', string='Parent Pharmacy')
    compliance_cert_no = fields.Char(string='License Number')
    active = fields.Boolean(default=True)

    # KPIs / smart button counts
    daily_sales_count = fields.Integer(
        string="Today's Sales",
        compute='_compute_kpis',
        help='Number of sales transactions processed today at this pharmacy branch.',
    )
    rx_count_today = fields.Integer(
        string='Prescriptions Today',
        compute='_compute_kpis',
        help='Number of prescriptions created today for this pharmacy branch.',
    )
    shortage_alerts_count = fields.Integer(
        string='Shortage Alerts',
        compute='_compute_kpis',
        help='Number of drugs below minimum stock threshold at this pharmacy.',
    )
    expiring_lots_count = fields.Integer(
        string='Expiring Lots',
        compute='_compute_kpis',
        help='Number of stock lots expiring within the next 30 days at this pharmacy.',
    )

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Pharmacy code must be unique per company.'),
    ]

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        """If no explicit location is set, derive it from the warehouse."""
        for rec in self:
            if rec.warehouse_id and not rec.location_id:
                rec.location_id = rec.warehouse_id.lot_stock_id

    @api.depends('company_id')
    def _compute_kpis(self):
        """Optimized KPI computation using read_group for better performance."""
        Prescription = self.env['pharmacy.prescription']
        Lot = self.env['stock.lot']
        today = fields.Date.today()
        future_date = today + relativedelta(days=30)
        
        # Batch prescription counts by pharmacy_id
        pharmacy_ids = self.ids
        rx_counts = {}
        if pharmacy_ids:
            rx_data = Prescription.read_group(
                [('pharmacy_id', 'in', pharmacy_ids), ('date_prescribed', '=', today)],
                ['pharmacy_id'],
                ['pharmacy_id'],
            )
            rx_counts = {item['pharmacy_id'][0]: item.get('__count', 0) for item in rx_data if item.get('pharmacy_id')}
        
        # Batch expiring lot counts by pharmacy_id
        expiring_counts = {}
        if pharmacy_ids:
            lot_data = Lot.read_group(
                [
                    ('pharmacy_id', 'in', pharmacy_ids),
                    ('expiry_date', '!=', False),
                    ('expiry_date', '>=', today),
                    ('expiry_date', '<=', future_date),
                ],
                ['pharmacy_id'],
                ['pharmacy_id'],
            )
            expiring_counts = {item['pharmacy_id'][0]: item.get('__count', 0) for item in lot_data if item.get('pharmacy_id')}
        
        # Batch shortage alerts (placeholder for now - will be wired to coverage later)
        shortage_counts = {}
        
        for rec in self:
            rec.rx_count_today = rx_counts.get(rec.id, 0)
            rec.daily_sales_count = 0  # Placeholder: no dedicated sales model yet
            rec.expiring_lots_count = expiring_counts.get(rec.id, 0)
            rec.shortage_alerts_count = shortage_counts.get(rec.id, 0)

    # Smart button actions
    def action_view_prescriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branch Prescriptions',
            'res_model': 'pharmacy.prescription',
            'view_mode': 'tree,form',
            'domain': [('pharmacy_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_treatments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branch Treatments',
            'res_model': 'hospital.treatment',
            'view_mode': 'kanban,tree,form',
            'domain': [('pharmacy_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_controlled_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branch Controlled Logs',
            'res_model': 'pharmacy.controlled.log',
            'view_mode': 'kanban,tree,form,pivot,graph',
            'domain': [('pharmacy_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_expiring_lots(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branch Expiring Lots',
            'res_model': 'stock.lot',
            'view_mode': 'tree,form',
            'domain': [
                ('pharmacy_id', '=', self.id),
                ('expiry_date', '!=', False),
            ],
            'target': 'current',
        }


class PharmacyConfig(models.Model):
    _name = 'pharmacy.config'
    _description = 'Pharmacy Configuration'
    _rec_name = 'name'

    name = fields.Char(compute='_compute_name', store=True)
    tax_included = fields.Boolean()
    localization_code = fields.Selection(selection=[
        ('us', 'US'), ('eu', 'EU'), ('in', 'India'), ('ae', 'UAE'), ('other', 'Other')
    ], default='other')
    allow_substitution = fields.Boolean(default=True)
    substitution_policy_id = fields.Many2one('pharmacy.substitution.map')
    default_expiry_days = fields.Integer()

    @api.depends('tax_included', 'localization_code', 'allow_substitution')
    def _compute_name(self):
        for rec in self:
            localization = dict(self._fields['localization_code'].selection).get(rec.localization_code, rec.localization_code or 'n/a')
            tax = 'Tax-Included' if rec.tax_included else 'Tax-Excluded'
            substitution = 'Subs-Allowed' if rec.allow_substitution else 'Subs-Blocked'
            rec.name = f"{localization} | {tax} | {substitution}"


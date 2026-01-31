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

from odoo import api, fields, models


class PharmacyAlertRule(models.Model):
    _name = 'pharmacy.alert.rule'
    _description = 'Pharmacy Alert Rule'
    _check_company_auto = True

    name = fields.Char(required=True)
    rule_type = fields.Selection([
        ('expiry', 'Expiry'), ('stock', 'Stock'), ('recall', 'Recall'), ('controlled', 'Controlled')
    ], required=True)
    threshold = fields.Float()
    active = fields.Boolean(default=True)
    message_template = fields.Text()
    
    # Scoping fields for targeted alert rules
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
        help='Company scope for this alert rule. If set, rule applies only to this company.',
    )
    hospital_id = fields.Many2one(
        'hospital.hospital',
        domain="[('company_id','=',company_id)]",
        help='Hospital scope for this alert rule. If set, rule applies only to this hospital.',
    )
    pharmacy_id = fields.Many2one(
        'pharmacy.pharmacy',
        domain="[('hospital_id','=',hospital_id)]",
        help='Pharmacy scope for this alert rule. If set, rule applies only to this pharmacy branch.',
    )
    drug_category_id = fields.Many2one(
        'pharmacy.drug.category',
        help='Drug category scope. If set, rule applies only to drugs in this category.',
    )
    drug_id = fields.Many2one(
        'pharmacy.drug',
        help='Specific drug scope. If set, rule applies only to this drug.',
    )


class PharmacySubstitutionMap(models.Model):
    _name = 'pharmacy.substitution.map'
    _description = 'Drug Substitution Map'
    _rec_name = 'name'
    _check_company_auto = True

    name = fields.Char(compute='_compute_name', store=True)
    brand_id = fields.Many2one('pharmacy.drug', required=True)
    generic_id = fields.Many2one('pharmacy.drug', required=True)
    approved = fields.Boolean(default=False)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
        help='Company scope for this substitution policy. If set, substitution applies only within this company.',
    )

    _sql_constraints = [
        ('brand_generic_uniq', 'unique(brand_id, generic_id)', 'A substitution mapping between the same brand and generic drug can only exist once.'),
    ]

    @api.depends('brand_id', 'generic_id', 'approved')
    def _compute_name(self):
        for rec in self:
            brand = rec.brand_id.name or ''
            generic = rec.generic_id.name or ''
            suffix = ' [Approved]' if rec.approved else ''
            rec.name = f"{brand} → {generic}{suffix}".strip()



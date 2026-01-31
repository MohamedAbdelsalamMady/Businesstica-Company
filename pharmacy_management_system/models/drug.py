from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PharmacyDrugCategory(models.Model):
    _name = 'pharmacy.drug.category'
    _description = 'Drug Category'

    name = fields.Char(required=True)
    code = fields.Char()
    controlled = fields.Boolean()
    description = fields.Text()


class PharmacyDrug(models.Model):
    _name = 'pharmacy.drug'
    _description = 'Drug'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    product_id = fields.Many2one('product.template', required=True)
    # Do not store the related name to avoid translation issues across languages
    name = fields.Char(related='product_id.name', readonly=True)
    drug_category_id = fields.Many2one('pharmacy.drug.category')
    is_prescription_required = fields.Boolean()
    controlled = fields.Boolean()
    storage_temp_min = fields.Float()
    storage_temp_max = fields.Float()
    ingredient_ids = fields.One2many('pharmacy.drug.ingredient', 'drug_id')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
        tracking=True,
    )
    hospital_ids = fields.Many2many(
        'hospital.hospital',
        'pharmacy_drug_hospital_rel',
        'drug_id',
        'hospital_id',
        string='Hospitals',
        tracking=True,
    )
    pharmacy_ids = fields.Many2many(
        'pharmacy.pharmacy',
        'pharmacy_drug_pharmacy_rel',
        'drug_id',
        'pharmacy_id',
        string='Pharmacies',
        tracking=True,
    )
    coverage_ids = fields.One2many(
        'pharmacy.drug.coverage',
        'drug_id',
        string='Hospital Coverage',
    )
    
    # Smart button counts
    prescription_count = fields.Integer(string='Prescriptions', compute='_compute_prescription_count')
    stock_qty_available = fields.Float(string='Available Stock', compute='_compute_stock_qty')
    # Use the same compute method and explicit compute_sudo on both fields
    expiry_alert_count = fields.Integer(
        string='Expiring Lots',
        compute='_compute_expiry_alerts',
        compute_sudo=True,
    )
    has_expiring_lots = fields.Boolean(
        string='Has Expiring Lots',
        compute='_compute_expiry_alerts',
        search='_search_expiring_lots',
        compute_sudo=True,
    )
    hospital_count = fields.Integer(string='Hospitals', compute='_compute_hospital_count')
    
    @api.depends('product_id')
    def _compute_prescription_count(self):
        for rec in self:
            rec.prescription_count = self.env['pharmacy.prescription.line'].search_count([
                ('drug_id', '=', rec.id)
            ])
    
    @api.depends('product_id')
    def _compute_stock_qty(self):
        for rec in self:
            if rec.product_id:
                product = self.env['product.product'].search([('product_tmpl_id', '=', rec.product_id.id)], limit=1)
                if product:
                    rec.stock_qty_available = product.qty_available
                else:
                    rec.stock_qty_available = 0
            else:
                rec.stock_qty_available = 0
    
    @api.depends('product_id')
    def _compute_expiry_alerts(self):
        for rec in self:
            if rec.product_id:
                product = self.env['product.product'].search([('product_tmpl_id', '=', rec.product_id.id)], limit=1)
                if product:
                    today = fields.Date.today()
                    future_date = today + relativedelta(days=30)
                    count = self.env['stock.lot'].search_count([
                        ('product_id', '=', product.id),
                        ('expiry_date', '!=', False),
                        ('expiry_date', '<=', future_date),
                        ('expiry_date', '>=', today)
                    ])
                    rec.expiry_alert_count = count
                    rec.has_expiring_lots = count > 0
                else:
                    rec.expiry_alert_count = 0
                    rec.has_expiring_lots = False
            else:
                rec.expiry_alert_count = 0
                rec.has_expiring_lots = False
    
    def _search_expiring_lots(self, operator, value):
        """Search for drugs with expiring lots"""
        today = fields.Date.today()
        future_date = today + relativedelta(days=30)
        lots = self.env['stock.lot'].search([
            ('expiry_date', '!=', False),
            ('expiry_date', '<=', future_date),
            ('expiry_date', '>=', today)
        ])
        product_ids = lots.mapped('product_id').ids
        if not product_ids:
            return [('id', '=', False)]
        # Get product templates from products
        products = self.env['product.product'].browse(product_ids)
        product_tmpl_ids = products.mapped('product_tmpl_id').ids
        if not product_tmpl_ids:
            return [('id', '=', False)]
        # Find drugs with these product templates
        drug_ids = self.env['pharmacy.drug'].search([
            ('product_id', 'in', product_tmpl_ids)
        ]).ids
        if operator == '=' and value:
            return [('id', 'in', drug_ids)] if drug_ids else [('id', '=', False)]
        elif operator == '=' and not value:
            all_drug_ids = self.env['pharmacy.drug'].search([]).ids
            return [('id', 'in', [d for d in all_drug_ids if d not in drug_ids])] if drug_ids else [('id', 'in', all_drug_ids)]
        return []
    
    def action_view_prescriptions(self):
        """Open related prescriptions"""
        self.ensure_one()
        line_ids = self.env['pharmacy.prescription.line'].search([('drug_id', '=', self.id)]).mapped('prescription_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'pharmacy.prescription',
            'domain': [('id', 'in', line_ids)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_stock(self):
        """Open stock for this drug"""
        self.ensure_one()
        if not self.product_id:
            return False
        product = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)], limit=1)
        if not product:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock',
            'res_model': 'stock.quant',
            'domain': [('product_id', '=', product.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_expiring_lots(self):
        """Open expiring lots"""
        self.ensure_one()
        if not self.product_id:
            return False
        product = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)], limit=1)
        if not product:
            return False
        today = fields.Date.today()
        future_date = today + relativedelta(days=30)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expiring Lots',
            'res_model': 'stock.lot',
            'domain': [
                ('product_id', '=', product.id),
                ('expiry_date', '!=', False),
                ('expiry_date', '<=', future_date),
                ('expiry_date', '>=', today)
            ],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    @api.depends('hospital_ids')
    def _compute_hospital_count(self):
        for rec in self:
            rec.hospital_count = len(rec.hospital_ids)

    def action_view_hospital_coverage(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hospital Coverage',
            'res_model': 'pharmacy.drug.coverage',
            'domain': [('drug_id', '=', self.id)],
            'view_mode': 'tree,form,graph,pivot',
            'target': 'current',
        }


class PharmacyDrugIngredient(models.Model):
    _name = 'pharmacy.drug.ingredient'
    _description = 'Drug Ingredient'

    name = fields.Char(required=True)
    strength = fields.Char()
    unit = fields.Char()
    drug_id = fields.Many2one('pharmacy.drug', required=True, ondelete='cascade')
    substitutable = fields.Boolean(default=True)


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    hospital_id = fields.Many2one('hospital.hospital')
    pharmacy_id = fields.Many2one('pharmacy.pharmacy')
    recall_flag = fields.Boolean()
    recall_reason = fields.Text()
    temp_log = fields.Json()
    expiry_date = fields.Date()


class PharmacyDrugCoverage(models.Model):
    _name = 'pharmacy.drug.coverage'
    _description = 'Drug Hospital Coverage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    drug_id = fields.Many2one('pharmacy.drug', required=True, ondelete='cascade', tracking=True)
    hospital_id = fields.Many2one('hospital.hospital', required=True, tracking=True)
    pharmacy_id = fields.Many2one('pharmacy.pharmacy', domain="[('hospital_id','=',hospital_id)]", tracking=True)
    company_id = fields.Many2one('res.company', related='drug_id.company_id', store=True, readonly=True)
    min_qty = fields.Float(default=0.0)
    target_qty = fields.Float(default=0.0)
    max_qty = fields.Float(default=0.0)
    current_qty = fields.Float(compute='_compute_current_qty', store=True)
    shortage_flag = fields.Boolean(compute='_compute_shortage_flag', store=True)
    has_expiring_lots = fields.Boolean(compute='_compute_has_expiring', store=True)
    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('drug_id.name', 'hospital_id.name', 'pharmacy_id.name')
    def _compute_display_name(self):
        for rec in self:
            parts = [rec.drug_id.display_name or rec.drug_id.name or '']
            if rec.hospital_id:
                parts.append(rec.hospital_id.display_name or rec.hospital_id.name or '')
            if rec.pharmacy_id:
                parts.append(rec.pharmacy_id.display_name or rec.pharmacy_id.name or '')
            rec.display_name = ' - '.join(filter(None, parts))

    @api.depends('drug_id', 'hospital_id', 'pharmacy_id')
    def _compute_current_qty(self):
        StockQuant = self.env['stock.quant']
        for rec in self:
            qty = 0.0
            if rec.drug_id and rec.hospital_id:
                product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', rec.drug_id.product_id.id)
                ], limit=1)
                if product:
                    domain = [('product_id', '=', product.id)]
                    if rec.pharmacy_id and rec.pharmacy_id.location_id:
                        domain.append(('location_id', 'child_of', rec.pharmacy_id.location_id.id))
                    elif rec.hospital_id.warehouse_id and rec.hospital_id.warehouse_id.lot_stock_id:
                        domain.append(('location_id', 'child_of', rec.hospital_id.warehouse_id.lot_stock_id.id))
                    qty = sum(quant.quantity for quant in StockQuant.search(domain))
            rec.current_qty = qty

    @api.depends('current_qty', 'min_qty')
    def _compute_shortage_flag(self):
        for rec in self:
            rec.shortage_flag = rec.current_qty < rec.min_qty if rec.min_qty else False

    @api.depends('drug_id', 'hospital_id', 'pharmacy_id')
    def _compute_has_expiring(self):
        StockLot = self.env['stock.lot']
        for rec in self:
            has_expiring = False
            if rec.drug_id and rec.hospital_id:
                product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', rec.drug_id.product_id.id)
                ], limit=1)
                if product:
                    today = fields.Date.today()
                    future_date = today + relativedelta(days=30)
                    domain = [
                        ('product_id', '=', product.id),
                        ('expiry_date', '!=', False),
                        ('expiry_date', '>=', today),
                        ('expiry_date', '<=', future_date),
                        ('hospital_id', '=', rec.hospital_id.id),
                    ]
                    if rec.pharmacy_id:
                        domain.append(('pharmacy_id', '=', rec.pharmacy_id.id))
                    has_expiring = bool(StockLot.search_count(domain))
            rec.has_expiring_lots = has_expiring

    _sql_constraints = [
        (
            'uniq_drug_hospital_pharmacy',
            'unique(drug_id, hospital_id, pharmacy_id)',
            'Drug coverage per hospital/pharmacy must be unique.'
        )
    ]


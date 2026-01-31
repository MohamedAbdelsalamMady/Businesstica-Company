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
from odoo.exceptions import UserError


class PharmacyPrescription(models.Model):
    _name = 'pharmacy.prescription'
    _description = 'Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    hospital_id = fields.Many2one('hospital.hospital', required=True, default=lambda self: self.env.user.default_hospital_id)
    pharmacy_id = fields.Many2one('pharmacy.pharmacy', domain="[('hospital_id','=',hospital_id)]")
    name = fields.Char(required=True, default=lambda self: self.env['ir.sequence'].next_by_code('pharmacy.prescription') or '/')
    company_id = fields.Many2one(
        'res.company',
        related='hospital_id.company_id',
        store=True,
        readonly=True,
        index=True,
        help='Company that owns this prescription. Derived from the hospital.',
    )
    patient_id = fields.Many2one('res.partner', domain="[('is_patient','=',True)]", required=True)
    doctor_id = fields.Many2one('res.partner', domain="[('is_doctor','=',True)]", required=True)
    date_prescribed = fields.Date(default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'), ('approved', 'Approved'), ('dispensed', 'Dispensed'), ('cancel', 'Canceled')
    ], default='draft', tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    line_ids = fields.One2many('pharmacy.prescription.line', 'prescription_id')
    picking_id = fields.Many2one('stock.picking', string='Delivery Picking', readonly=True, copy=False)
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        readonly=True,
        copy=False,
        domain="[('move_type','=','out_invoice')]",
        help='Customer invoice generated for this prescription.',
    )
    
    # Smart button counts
    claim_count = fields.Integer(string='Claims', compute='_compute_claim_count')
    controlled_log_count = fields.Integer(string='Controlled Logs', compute='_compute_controlled_log_count')
    
    # Pivot view count field
    count_field = fields.Integer(string='Count', compute='_compute_count_field', store=True, default=1)
    
    def _compute_count_field(self):
        for rec in self:
            rec.count_field = 1
    
    # Search fields
    drug_ids = fields.Many2many('pharmacy.drug', string='Drugs', compute='_compute_drug_ids', search='_search_drug_ids', store=False)
    
    @api.depends('line_ids.drug_id')
    def _compute_drug_ids(self):
        for rec in self:
            rec.drug_ids = rec.line_ids.mapped('drug_id')
    
    def _search_drug_ids(self, operator, value):
        """Search prescriptions by drug"""
        if isinstance(value, str):
            # Search by drug name
            drug_ids = self.env['pharmacy.drug'].search([
                ('name', 'ilike', value)
            ]).ids
            line_ids = self.env['pharmacy.prescription.line'].search([
                ('drug_id', 'in', drug_ids)
            ]).mapped('prescription_id').ids
        else:
            # Search by drug ID
            line_ids = self.env['pharmacy.prescription.line'].search([
                ('drug_id', operator, value)
            ]).mapped('prescription_id').ids
        return [('id', 'in', line_ids)] if line_ids else [('id', '=', False)]
    
    @api.depends('name')
    def _compute_claim_count(self):
        for rec in self:
            rec.claim_count = self.env['pharmacy.insurance.claim'].search_count([('prescription_id', '=', rec.id)])
    
    @api.depends('line_ids.drug_id')
    def _compute_controlled_log_count(self):
        for rec in self:
            drug_ids = rec.line_ids.mapped('drug_id').ids
            rec.controlled_log_count = self.env['pharmacy.controlled.log'].search_count([
                ('drug_id', 'in', drug_ids),
                ('hospital_id', '=', rec.hospital_id.id),
                ('pharmacy_id', '=', rec.pharmacy_id.id)
            ])

    # -------------------------------------------------------------------------
    # Invoicing helpers
    # -------------------------------------------------------------------------

    def _prepare_invoice_vals(self):
        """Prepare values for an out_invoice based on this prescription."""
        self.ensure_one()
        if not self.patient_id:
            raise UserError("Please set a patient before creating an invoice.")
        if not self.line_ids:
            raise UserError("Cannot create invoice: no prescription lines found.")

        # Find a sales journal for this company
        Journal = self.env['account.journal']
        journal = Journal.search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        if not journal:
            raise UserError("No Sales journal found for this company. Please configure an accounting Sales journal.")

        invoice_lines = []
        for line in self.line_ids:
            if not line.drug_id or not line.drug_id.product_id:
                continue
            # Use full dispensed quantity if any, otherwise prescribed
            qty = line.qty_dispensed or line.qty_prescribed
            if not qty:
                continue
            product_tmpl = line.drug_id.product_id
            product_variant = self._get_variant(product_tmpl)
            invoice_lines.append((0, 0, {
                'product_id': product_variant.id,
                'name': line.drug_id.name or product_variant.display_name,
                'quantity': qty,
                'price_unit': product_variant.lst_price,
            }))

        if not invoice_lines:
            raise UserError("Cannot create invoice: no billable quantities on prescription lines.")

        return {
            'move_type': 'out_invoice',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'partner_id': self.patient_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
        }

    def action_create_invoice(self):
        """Create an invoice for the prescription, if not already created."""
        Move = self.env['account.move']
        for rec in self:
            if rec.invoice_id:
                continue
            vals = rec._prepare_invoice_vals()
            invoice = Move.create(vals)
            rec.invoice_id = invoice.id
        return True

    def action_view_invoice(self):
        """Open the related invoice, creating it first if necessary."""
        self.ensure_one()
        if not self.invoice_id:
            self.action_create_invoice()
        if not self.invoice_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def action_approve(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Only draft prescriptions can be approved.")
            rec.state = 'approved'

    def action_cancel(self):
        """Cancel prescription"""
        for rec in self:
            if rec.state in ('cancel', 'dispensed'):
                raise UserError("Cannot cancel a prescription that is already canceled or dispensed.")
            rec.state = 'cancel'

    def _get_variant(self, product_tmpl):
        Product = self.env['product.product']
        variant = Product.search([('product_tmpl_id', '=', product_tmpl.id)], limit=1)
        if not variant:
            raise UserError(f"No product variant found for template {product_tmpl.display_name}.")
        return variant

    def _prepare_picking_vals(self):
        self.ensure_one()
        if not self.pharmacy_id:
            raise UserError("Please set a Pharmacy on the prescription.")
        warehouse = self.pharmacy_id.warehouse_id or self.hospital_id.warehouse_id
        if not warehouse:
            raise UserError("No warehouse configured on the Pharmacy or Hospital.")
        if not warehouse.out_type_id:
            raise UserError(f"Warehouse {warehouse.display_name} has no outgoing picking type.")
        partner = self.patient_id
        customer_loc = partner.property_stock_customer or self.env.ref('stock.stock_location_customers')
        return {
            'origin': self.name,
            'picking_type_id': warehouse.out_type_id.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': customer_loc.id,
            'partner_id': partner.id,
        }

    def _create_moves_for_picking(self, picking):
        Move = self.env['stock.move']
        for line in self.line_ids:
            qty_remaining = max(0.0, (line.qty_prescribed or 0.0) - (line.qty_dispensed or 0.0))
            if qty_remaining <= 0:
                continue
            variant = self._get_variant(line.drug_id.product_id)
            Move.create({
                'name': line.drug_id.name or variant.display_name,
                'product_id': variant.id,
                'product_uom': (line.uom_id and line.uom_id.id) or variant.uom_id.id,
                'product_uom_qty': qty_remaining,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'description_picking': line.dosage or '',
            })

    def action_create_picking(self):
        for rec in self:
            if rec.picking_id:
                continue
            # Check if there are any prescription lines
            if not rec.line_ids:
                raise UserError("Cannot create delivery: No prescription lines found. Please add drugs to the prescription first.")
            # Check if there's any quantity to dispense
            has_qty_to_dispense = False
            for line in rec.line_ids:
                qty_remaining = max(0.0, (line.qty_prescribed or 0.0) - (line.qty_dispensed or 0.0))
                if qty_remaining > 0:
                    has_qty_to_dispense = True
                    break
            if not has_qty_to_dispense:
                raise UserError("Cannot create delivery: All prescription lines are already fully dispensed or have no quantity to dispense.")
            picking_vals = rec._prepare_picking_vals()
            picking = self.env['stock.picking'].create(picking_vals)
            rec._create_moves_for_picking(picking)
            # Check if any moves were actually created
            if not picking.move_ids:
                picking.unlink()
                raise UserError("Cannot create delivery: No valid moves could be created. Please check prescription line quantities.")
            rec.picking_id = picking.id
        return True

    def action_dispense(self):
        """Mark as dispensed and set qty_dispensed to prescribed (full dispense).
        Use picking for logistics; this simply updates business state/quantities.
        """
        for rec in self:
            if rec.state not in ('approved', 'partial', 'dispensed'):
                raise UserError("Prescription must be approved before dispensing.")
            # Ensure a picking exists for traceability
            if not rec.picking_id:
                rec.action_create_picking()
            for line in rec.line_ids:
                qty_remaining = max(0.0, (line.qty_prescribed or 0.0) - (line.qty_dispensed or 0.0))
                if qty_remaining > 0:
                    line.qty_dispensed = (line.qty_dispensed or 0.0) + qty_remaining
            rec.state = 'dispensed'
        return True

    def action_view_picking(self):
        """Open the related picking"""
        self.ensure_one()
        if not self.picking_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery Picking',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_claims(self):
        """Open related insurance claims"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Insurance Claims',
            'res_model': 'pharmacy.insurance.claim',
            'domain': [('prescription_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_view_controlled_logs(self):
        """Open related controlled logs"""
        self.ensure_one()
        drug_ids = self.line_ids.mapped('drug_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Controlled Logs',
            'res_model': 'pharmacy.controlled.log',
            'domain': [
                ('drug_id', 'in', drug_ids),
                ('hospital_id', '=', self.hospital_id.id),
                ('pharmacy_id', '=', self.pharmacy_id.id)
            ],
            'view_mode': 'tree,form',
            'target': 'current',
        }


class PharmacyPrescriptionLine(models.Model):
    _name = 'pharmacy.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one('pharmacy.prescription', required=True, ondelete='cascade')
    hospital_id = fields.Many2one(related='prescription_id.hospital_id', store=True)
    pharmacy_id = fields.Many2one(related='prescription_id.pharmacy_id', store=True)
    company_id = fields.Many2one(
        'res.company',
        related='prescription_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
    drug_id = fields.Many2one('pharmacy.drug', required=True)
    dosage = fields.Char()
    qty_prescribed = fields.Float(default=1.0)
    qty_dispensed = fields.Float(readonly=True)
    uom_id = fields.Many2one('uom.uom')

    @api.constrains('qty_dispensed', 'qty_prescribed')
    def _check_dispensed_qty(self):
        """Ensure dispensed quantity does not exceed prescribed quantity."""
        for rec in self:
            if rec.qty_dispensed and rec.qty_prescribed:
                if rec.qty_dispensed > rec.qty_prescribed:
                    raise models.ValidationError(
                        f'Dispensed quantity ({rec.qty_dispensed}) cannot exceed prescribed quantity ({rec.qty_prescribed}) for drug {rec.drug_id.name or "N/A"}.'
                    )


class PharmacyReturnQuarantine(models.Model):
    _name = 'pharmacy.return.quarantine'
    _description = 'Return Quarantine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(required=True, default=lambda self: self.env['ir.sequence'].next_by_code('pharmacy.return.quarantine') or '/')
    drug_id = fields.Many2one('pharmacy.drug', required=True)
    hospital_id = fields.Many2one(
        'hospital.hospital',
        help='Hospital associated with this return. Can be selected from hospitals where this drug has coverage.',
    )
    pharmacy_id = fields.Many2one(
        'pharmacy.pharmacy',
        domain="[('hospital_id','=',hospital_id)]",
        help='Pharmacy branch handling this return.',
    )
    company_id = fields.Many2one(
        'res.company',
        related='drug_id.company_id',
        store=True,
        readonly=True,
        index=True,
        help='Company that owns this return. Derived from the drug.',
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Source Invoice',
        domain="[('move_type','=','out_invoice')]",
        help='Customer invoice from which this product is being returned.',
    )
    refund_id = fields.Many2one(
        'account.move',
        string='Refund Invoice',
        readonly=True,
        copy=False,
        domain="[('move_type','=','out_refund')]",
        help='Refund/credit note generated for this return.',
    )
    qty = fields.Float(required=True)
    reason = fields.Text()
    state = fields.Selection([('awaiting', 'Awaiting'), ('disposed', 'Disposed')], default='awaiting', tracking=True)

    @api.constrains('qty')
    def _check_qty_positive(self):
        """Ensure quantity is positive."""
        for rec in self:
            if rec.qty <= 0:
                raise models.ValidationError('Return quantity must be greater than zero.')

    def _prepare_refund_vals(self):
        """Prepare values for an out_refund based on this return."""
        self.ensure_one()
        if not self.invoice_id:
            raise UserError("Please set a source invoice on the return before creating a refund.")
        if not self.drug_id or not self.drug_id.product_id:
            raise UserError("Return must have a drug linked to a product to create a refund.")
        if self.qty <= 0:
            raise UserError("Return quantity must be greater than zero to create a refund.")

        # Use patient / invoice partner
        partner = self.invoice_id.partner_id
        if not partner:
            raise UserError("Source invoice has no customer/partner set.")

        # Use same journal as original invoice
        journal = self.invoice_id.journal_id
        if not journal:
            raise UserError("Source invoice has no journal set.")

        product_tmpl = self.drug_id.product_id
        product_variant = self.env['product.product'].search(
            [('product_tmpl_id', '=', product_tmpl.id)],
            limit=1,
        )
        if not product_variant:
            raise UserError(f"No product variant found for drug {self.drug_id.display_name}.")

        line_vals = (0, 0, {
            'product_id': product_variant.id,
            'name': self.drug_id.name or product_variant.display_name,
            'quantity': self.qty,
            'price_unit': product_variant.lst_price,
        })

        return {
            'move_type': 'out_refund',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'partner_id': partner.id,
            'invoice_origin': self.name,
            'reversed_entry_id': self.invoice_id.id,
            'invoice_line_ids': [line_vals],
        }

    def action_create_refund(self):
        """Create a refund (credit note) for this return."""
        Move = self.env['account.move']
        for rec in self:
            if rec.refund_id:
                continue
            vals = rec._prepare_refund_vals()
            refund = Move.create(vals)
            rec.refund_id = refund.id
        return True

    def action_dispose(self):
        """Mark return/quarantine as disposed"""
        for rec in self:
            if rec.state != 'awaiting':
                raise UserError("Only awaiting items can be marked as disposed.")
            rec.state = 'disposed'

    def action_view_refund(self):
        """Open the related refund, creating it first if necessary."""
        self.ensure_one()
        if not self.refund_id:
            self.action_create_refund()
        if not self.refund_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Refund Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.refund_id.id,
            'target': 'current',
        }



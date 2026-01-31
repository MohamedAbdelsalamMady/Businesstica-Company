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

import base64
import binascii

from odoo import _, api, fields, models


class HospitalTreatmentStage(models.Model):
    _name = 'hospital.treatment.stage'
    _description = 'Treatment Stage'
    _order = 'sequence, id'
    _check_company_auto = True

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    is_default = fields.Boolean()
    is_closed = fields.Boolean()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    description = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.is_default:
                others = self.search([
                    ('company_id', '=', record.company_id.id),
                    ('id', '!=', record.id),
                    ('is_default', '=', True),
                ])
                others.write({'is_default': False})
        return records


class HospitalTreatment(models.Model):
    _name = 'hospital.treatment'
    _description = 'Treatment Episode'
    _order = 'start_datetime desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    _TOKEN_FIELDS = {
        'telemedicine_session_id',
        'telemedicine_session_url',
        'telemedicine_join_token',
    }

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('hospital.treatment') or '/',
        required=True,
        copy=False,
        tracking=True,
    )
    patient_id = fields.Many2one(
        'res.partner',
        domain="[('is_patient','=',True)]",
        required=True,
        tracking=True,
    )
    hospital_id = fields.Many2one(
        'hospital.hospital',
        required=True,
        tracking=True,
    )
    pharmacy_id = fields.Many2one(
        'pharmacy.pharmacy',
        domain="[('hospital_id','=',hospital_id)]",
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='hospital_id.company_id',
        store=True,
        readonly=False,
        index=True,
    )
    responsible_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        tracking=True,
    )
    stage_id = fields.Many2one(
        'hospital.treatment.stage',
        tracking=True,
        default=lambda self: self._default_stage_id(),
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    start_datetime = fields.Datetime(default=fields.Datetime.now, tracking=True)
    end_datetime = fields.Datetime(tracking=True)
    duration_hours = fields.Float(compute='_compute_duration', store=True)
    
    # Pivot view count field
    count_field = fields.Integer(string='Count', compute='_compute_count_field', store=True, default=1)
    
    def _compute_count_field(self):
        for rec in self:
            rec.count_field = 1
    vitals_snapshot = fields.Json()
    notes = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    prescription_ids = fields.Many2many(
        'pharmacy.prescription',
        'hospital_treatment_prescription_rel',
        'treatment_id',
        'prescription_id',
        string='Prescriptions',
    )
    prescription_count = fields.Integer(compute='_compute_prescription_count')
    activity_log = fields.Text(help="Concise log of key status changes for audit summaries.")
    telemedicine_enabled = fields.Boolean(default=False, tracking=True)
    telemedicine_session_id = fields.Char()
    telemedicine_session_url = fields.Char()
    telemedicine_join_token = fields.Char()
    telemedicine_last_access = fields.Datetime()
    portal_visible = fields.Boolean(default=True)
    compliance_flagged = fields.Boolean(default=False, tracking=True)

    _sql_constraints = [
        ('unique_name_company', 'unique(name, company_id)', 'Treatment reference must be unique per company.'),
    ]

    @api.model
    def _default_stage_id(self):
        company = self.env.company
        default_stage = self.env['hospital.treatment.stage'].search([
            ('company_id', '=', company.id),
            ('is_default', '=', True),
        ], limit=1)
        if default_stage:
            return default_stage.id
        any_stage = self.env['hospital.treatment.stage'].search([
            ('company_id', '=', company.id)
        ], order='sequence asc', limit=1)
        return any_stage.id

    @staticmethod
    def _encode_base64_value(value):
        if not value:
            return value
        if isinstance(value, bytes):
            raw = value
        else:
            raw = str(value).encode('utf-8')
        try:
            base64.b64decode(raw, validate=True)
            return raw.decode('utf-8')
        except (binascii.Error, ValueError):
            encoded = base64.b64encode(raw)
            return encoded.decode('utf-8')

    @api.model
    def _normalize_token_values(self, vals):
        for field in self._TOKEN_FIELDS:
            if vals.get(field):
                vals[field] = self._encode_base64_value(vals[field])
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        normalized = [self._normalize_token_values(vals.copy()) for vals in vals_list]
        now = fields.Datetime.now()
        for vals in normalized:
            if any(vals.get(field) for field in self._TOKEN_FIELDS) and 'telemedicine_last_access' not in vals:
                vals['telemedicine_last_access'] = now
        for vals in normalized:
            if 'stage_id' in vals and 'state' not in vals:
                stage = self.env['hospital.treatment.stage'].browse(vals['stage_id'])
                if stage and stage.is_closed:
                    vals['state'] = 'done'
                elif stage:
                    vals['state'] = 'active'
        treatments = super().create(normalized)
        for treatment in treatments:
            if treatment.stage_id and treatment.stage_id.is_closed and treatment.state != 'done':
                treatment.state = 'done'
        return treatments

    def write(self, vals):
        normalized_vals = self._normalize_token_values(vals.copy())
        if any(field in normalized_vals for field in self._TOKEN_FIELDS) and 'telemedicine_last_access' not in normalized_vals:
            normalized_vals['telemedicine_last_access'] = fields.Datetime.now()
        if 'stage_id' in normalized_vals and normalized_vals.get('state') != 'cancelled':
            stage = self.env['hospital.treatment.stage'].browse(normalized_vals['stage_id']) if normalized_vals['stage_id'] else None
            if stage and stage.is_closed:
                normalized_vals.setdefault('state', 'done')
            elif stage:
                normalized_vals.setdefault('state', 'active')
            else:
                normalized_vals.setdefault('state', 'draft')
        stage_changed_records = self.filtered(lambda rec: 'stage_id' in normalized_vals and normalized_vals['stage_id'] != rec.stage_id.id)
        result = super().write(normalized_vals)
        if 'stage_id' in normalized_vals:
            for rec in stage_changed_records:
                rec.message_post(
                    body=_("Stage changed to %s") % (rec.stage_id.display_name or _("Unknown Stage"))
                )
        if any(field in normalized_vals for field in self._TOKEN_FIELDS):
            for rec in self:
                rec.message_post(body=_("Telemedicine session metadata updated."))
        return result

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for rec in self:
            duration = 0.0
            if rec.start_datetime and rec.end_datetime and rec.end_datetime >= rec.start_datetime:
                start = fields.Datetime.to_datetime(rec.start_datetime)
                end = fields.Datetime.to_datetime(rec.end_datetime)
                delta = end - start
                duration = delta.total_seconds() / 3600.0
            rec.duration_hours = duration

    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        for rec in self:
            rec.prescription_count = len(rec.prescription_ids)

    def action_open_prescriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Treatment Prescriptions'),
            'res_model': 'pharmacy.prescription',
            'domain': [('id', 'in', self.prescription_ids.ids)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_mark_active(self):
        for rec in self:
            rec.state = 'active'

    def action_mark_done(self):
        done_stage = self.env['hospital.treatment.stage'].search([
            ('company_id', '=', self.company_id.id),
            ('is_closed', '=', True),
        ], limit=1)
        for rec in self:
            if done_stage:
                rec.stage_id = done_stage.id
            rec.state = 'done'
            rec.message_post(body=_("Treatment marked as completed."))

    def action_mark_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'
            rec.message_post(body=_("Treatment cancelled."))

    def action_toggle_portal_visibility(self):
        for rec in self:
            rec.portal_visible = not rec.portal_visible
            status = "enabled" if rec.portal_visible else "disabled"
            rec.message_post(body=_("Portal visibility %s.") % status)

    def action_flag_compliance(self):
        for rec in self:
            rec.compliance_flagged = True
            rec.message_post(body=_("Treatment flagged for compliance follow-up."))

    def action_clear_compliance(self):
        for rec in self:
            rec.compliance_flagged = False
            rec.message_post(body=_("Compliance flag cleared."))



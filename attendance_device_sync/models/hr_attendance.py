from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Many2one(
        'attendance.device',
        string='Device',
        readonly=True,
        help='Biometric device that recorded this attendance'
    )
    device_timestamp = fields.Datetime(
        string='Device Timestamp',
        readonly=True,
        help='Original timestamp from device'
    )
    is_from_device = fields.Boolean(
        string='From Device',
        default=False,
        readonly=True
    )
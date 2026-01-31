from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    device_user_id = fields.Char(
        string='Device User ID',
        help='Unique ID for biometric device',
        copy=False,
        index=True
    )
    synced_to_device = fields.Boolean(
        string='Synced to Device',
        default=False,
        copy=False
    )
    last_device_sync = fields.Datetime(
        string='Last Device Sync',
        copy=False,
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-generate device_user_id for new employees"""
        for vals in vals_list:
            if not vals.get('device_user_id'):
                vals['device_user_id'] = self._generate_device_user_id()
        employees = super(HrEmployee, self).create(vals_list)
        employees._trigger_device_sync()
        return employees

    def write(self, vals):
        """Detect changes and trigger sync"""
        name_changed = 'name' in vals
        result = super(HrEmployee, self).write(vals)
        if name_changed or 'device_user_id' in vals:
            self._trigger_device_sync()
        return result

    @api.model
    def _generate_device_user_id(self):
        """Generate unique device user ID"""
        last_employee = self.search(
            [('device_user_id', '!=', False)],
            order='device_user_id desc',
            limit=1
        )
        if last_employee and last_employee.device_user_id.isdigit():
            new_id = int(last_employee.device_user_id) + 1
        else:
            new_id = 1  # تم التعديل هنا: البداية من 1 بدلاً من 1000
        return str(new_id)

    def _trigger_device_sync(self):
        """Trigger device synchronization"""
        devices = self.env['attendance.device'].search([('active', '=', True)])
        if devices:
            devices[0].sync_employees_to_device(self)

    @api.model
    def ensure_all_have_device_ids(self):
        """Ensure all employees have device_user_id"""
        employees_without_id = self.search([
            ('device_user_id', '=', False),
            ('active', '=', True)
        ])

        for employee in employees_without_id:
            employee.device_user_id = self._generate_device_user_id()
            _logger.info(f'Generated device_user_id {employee.device_user_id} for {employee.name}')

        return len(employees_without_id)

# from odoo import models, fields, api
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
#
#     device_user_id = fields.Char(
#         string='Device User ID',
#         help='Unique ID for biometric device',
#         copy=False,
#         index=True
#     )
#     synced_to_device = fields.Boolean(
#         string='Synced to Device',
#         default=False,
#         copy=False
#     )
#     last_device_sync = fields.Datetime(
#         string='Last Device Sync',
#         copy=False,
#         readonly=True
#     )
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         """Auto-generate device_user_id for new employees"""
#         for vals in vals_list:
#             if not vals.get('device_user_id'):
#                 vals['device_user_id'] = self._generate_device_user_id()
#         employees = super(HrEmployee, self).create(vals_list)
#         employees._trigger_device_sync()
#         return employees
#
#     def write(self, vals):
#         """Detect changes and trigger sync"""
#         name_changed = 'name' in vals
#         result = super(HrEmployee, self).write(vals)
#         if name_changed or 'device_user_id' in vals:
#             self._trigger_device_sync()
#         return result
#
#     @api.model
#     def _generate_device_user_id(self):
#         """Generate unique device user ID"""
#         last_employee = self.search(
#             [('device_user_id', '!=', False)],
#             order='device_user_id desc',
#             limit=1
#         )
#         if last_employee and last_employee.device_user_id.isdigit():
#             new_id = int(last_employee.device_user_id) + 1
#         else:
#             new_id = 1000
#         return str(new_id)
#
#     def _trigger_device_sync(self):
#         """Trigger device synchronization"""
#         devices = self.env['attendance.device'].search([('active', '=', True)])
#         if devices:
#             devices[0].sync_employees_to_device(self)
#
#     @api.model
#     def ensure_all_have_device_ids(self):
#         """Ensure all employees have device_user_id"""
#         employees_without_id = self.search([
#             ('device_user_id', '=', False),
#             ('active', '=', True)
#         ])
#
#         for employee in employees_without_id:
#             employee.device_user_id = self._generate_device_user_id()
#             _logger.info(f'Generated device_user_id {employee.device_user_id} for {employee.name}')
#
#         return len(employees_without_id)
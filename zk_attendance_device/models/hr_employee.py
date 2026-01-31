# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # ZK device user ID
    device_user_id = fields.Char(
        string='Device User ID',
        help='The user identifier used in the ZK fingerprint device',
        copy=False
    )

    @api.constrains('device_user_id')
    def _check_device_user_id(self):
        """Validate that the device user ID is numeric and unique"""
        for employee in self:
            if employee.device_user_id:
                # Check if the ID is numeric
                try:
                    int(employee.device_user_id)
                except ValueError:
                    raise ValidationError('Device User ID must be a number')

                # Check uniqueness
                duplicate = self.search([
                    ('device_user_id', '=', employee.device_user_id),
                    ('id', '!=', employee.id)
                ], limit=1)

                if duplicate:
                    raise ValidationError(
                        f'Device ID {employee.device_user_id} is already assigned to employee {duplicate.name}'
                    )

# # -*- coding: utf-8 -*-
# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
#
# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
#
#     device_user_id = fields.Char(
#         string='معرف المستخدم في الجهاز',
#         help='المعرف المستخدم في جهاز البصمة ZK',
#         copy=False
#     )
#
#     @api.constrains('device_user_id')
#     def _check_device_user_id(self):
#         for employee in self:
#             if employee.device_user_id:
#                 # التحقق من أن المعرف رقم
#                 try:
#                     int(employee.device_user_id)
#                 except ValueError:
#                     raise ValidationError('معرف المستخدم في الجهاز يجب أن يكون رقماً')
#
#                 # التحقق من عدم التكرار
#                 duplicate = self.search([
#                     ('device_user_id', '=', employee.device_user_id),
#                     ('id', '!=', employee.id)
#                 ], limit=1)
#
#                 if duplicate:
#                     raise ValidationError(
#                         f'معرف الجهاز {employee.device_user_id} مستخدم بالفعل للموظف {duplicate.name}'
#                     )
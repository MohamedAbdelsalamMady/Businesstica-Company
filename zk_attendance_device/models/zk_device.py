# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime, timedelta
from zk import ZK
import pytz

_logger = logging.getLogger(__name__)


class ZKDevice(models.Model):
    _name = 'zk.device'
    _description = 'ZK Fingerprint Device'
    _inherit = ['mail.thread', 'mail.activity.mixin']   # Important line
    _order = 'name'

    # Device Info
    name = fields.Char('Device Name', required=True)
    ip_address = fields.Char('IP Address', required=True)
    port = fields.Integer('Port', default=4370, required=True)
    timeout = fields.Integer('Timeout (seconds)', default=5)
    timezone = fields.Selection(
        '_get_timezone_list',
        string='Timezone',
        default='Africa/Cairo',
        required=True,
        help='Device timezone for attendance records'
    )

    # Sync Settings
    sync_users = fields.Boolean('Sync Users', default=True,
                                help='Sync Odoo employees to the device')
    sync_users_interval = fields.Integer('User Sync Interval (minutes)', default=60)
    sync_attendance = fields.Boolean('Sync Attendance', default=True)
    sync_attendance_interval = fields.Integer('Attendance Sync Interval (seconds)', default=10)

    # Connection State
    state = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected'),
        ('syncing', 'Syncing'),
        ('error', 'Error')
    ], string='State', default='disconnected', readonly=True)

    last_sync_time = fields.Datetime('Last Sync', readonly=True)
    last_user_sync_time = fields.Datetime('Last User Sync', readonly=True)
    last_error = fields.Text('Last Error', readonly=True)

    # Device Details
    # device_name = fields.Char('Actual Device Name', readonly=True)
    # serial_number = fields.Char('Serial Number', readonly=True)
    # firmware_version = fields.Char('Firmware Version', readonly=True)
    total_users = fields.Integer('Total Users', readonly=True)

    # Relations
    sync_log_ids = fields.One2many('zk.sync.log', 'device_id', string='Sync Logs')
    sync_log_count = fields.Integer('Log Count', compute='_compute_sync_log_count')

    # Attendance Settings
    checkin_status = fields.Integer('Check-in Status', default=0,
                                    help='Value used by device for check-in')
    checkout_status = fields.Integer('Check-out Status', default=1,
                                     help='Value used by device for check-out')

    active = fields.Boolean('Active', default=True)

    @api.depends('sync_log_ids')
    def _compute_sync_log_count(self):
        for device in self:
            device.sync_log_count = len(device.sync_log_ids)

    @api.model
    def _get_timezone_list(self):
        """Get list of timezones"""
        return [(tz, tz) for tz in pytz.all_timezones]

    @api.constrains('ip_address', 'port')
    def _check_connection_params(self):
        for device in self:
            if not device.ip_address:
                raise ValidationError(_('IP Address is required'))
            if device.port <= 0 or device.port > 65535:
                raise ValidationError(_('Port number must be between 1 and 65535'))

    def _get_zk_connection(self):
        """Create a connection to the ZK device"""
        self.ensure_one()
        zk = ZK(self.ip_address, port=self.port, timeout=self.timeout, ommit_ping=True)
        try:
            conn = zk.connect()
            conn.disable_device()
            return conn
        except Exception as e:
            _logger.error(f"Failed to connect to device {self.name}: {e}")
            raise UserError(_('Failed to connect to the device: %s') % str(e))

    def _disconnect_zk(self, conn):
        """Disconnect from ZK device"""
        try:
            if conn:
                conn.enable_device()
                conn.disconnect()
        except Exception as e:
            _logger.warning(f"Error disconnecting: {e}")

    def action_test_connection(self):
        """Test connection to the device"""
        self.ensure_one()
        conn = None
        try:
            conn = self._get_zk_connection()

            # Get device info
            try:
                device_name = conn.get_device_name() or 'Unknown'
                serial_number = conn.get_serialnumber() or 'Unknown'
                firmware = conn.get_firmware_version() or 'Unknown'
                users = conn.get_users()

                self.write({
                    'state': 'connected',
                    'device_name': device_name,
                    'serial_number': serial_number,
                    'firmware_version': firmware,
                    'total_users': len(users),
                    'last_error': False,
                })
            except Exception:
                self.state = 'connected'

            self._disconnect_zk(conn)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _('Device connected successfully'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.write({
                'state': 'error',
                'last_error': str(e),
            })
            if conn:
                self._disconnect_zk(conn)
            raise UserError(_('Connection failed: %s') % str(e))

    def action_sync_users(self):
        """Sync users from Odoo to device"""
        self.ensure_one()
        if not self.sync_users:
            raise UserError(_('User sync is not enabled for this device'))
        return self._sync_users_to_device()

    def _sync_users_to_device(self):
        """Perform the actual user sync"""
        self.ensure_one()
        conn = None
        sync_log = self.env['zk.sync.log'].create({
            'device_id': self.id,
            'sync_type': 'user',
            'state': 'running',
        })

        try:
            self.state = 'syncing'
            conn = self._get_zk_connection()

            employees = self.env['hr.employee'].search([
                ('device_user_id', '!=', False)
            ])

            if not employees:
                sync_log.write({
                    'state': 'warning',
                    'message': 'No employees with device_user_id',
                })
                self.state = 'connected'
                self._disconnect_zk(conn)
                return

            device_users = conn.get_users()
            device_user_dict = {
                (getattr(u, 'user_id', None) or getattr(u, 'uid', None)):
                    (getattr(u, 'name', '') or getattr(u, 'username', ''))
                for u in device_users
            }

            created = 0
            updated = 0
            errors = 0

            for emp in employees:
                try:
                    device_id = int(emp.device_user_id)
                    emp_name = emp.name[:24]

                    # Always use set_user - it will create if not exists, or update if exists
                    conn.set_user(
                        uid=device_id,
                        name=emp_name,
                        privilege=0,
                        password='',
                        group_id='',
                        user_id=str(device_id)
                    )
                    
                    if device_id in device_user_dict:
                        updated += 1
                        _logger.info(f"Updated user {device_id}: {emp_name}")
                    else:
                        created += 1
                        _logger.info(f"Created user {device_id}: {emp_name}")

                except Exception as e:
                    errors += 1
                    _logger.error(f"Error syncing employee {emp.name}: {e}")

            message = f"Sync result:\n- Created: {created}\n- Updated: {updated}\n- Errors: {errors}"

            sync_log.write({
                'state': 'success' if errors == 0 else 'warning',
                'message': message,
                'records_processed': created + updated,
            })

            self.write({
                'state': 'connected',
                'last_user_sync_time': fields.Datetime.now(),
                'total_users': len(device_users) + created,
            })

            self._disconnect_zk(conn)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            error_msg = str(e)
            sync_log.write({
                'state': 'error',
                'message': error_msg,
            })
            self.write({
                'state': 'error',
                'last_error': error_msg,
            })
            if conn:
                self._disconnect_zk(conn)
            raise UserError(_('User sync failed: %s') % error_msg)

    def action_sync_attendance(self):
        """Sync attendance records from device"""
        self.ensure_one()
        if not self.sync_attendance:
            raise UserError(_('Attendance sync is not enabled for this device'))
        return self._sync_attendance_from_device()

    def _sync_attendance_from_device(self, after_timestamp=None):
        """Perform the actual attendance sync"""
        self.ensure_one()
        conn = None
        sync_log = self.env['zk.sync.log'].create({
            'device_id': self.id,
            'sync_type': 'attendance',
            'state': 'running',
        })

        try:
            self.state = 'syncing'
            conn = self._get_zk_connection()

            attendances = conn.get_attendance()
            if not attendances:
                sync_log.write({
                    'state': 'success',
                    'message': 'No new attendance records',
                })
                self.state = 'connected'
                self._disconnect_zk(conn)
                return

            records = []
            for att in attendances:
                device_user_id = getattr(att, 'user_id', None) or getattr(att, 'uid', None)
                timestamp = att.timestamp
                status = getattr(att, 'status', None)

                if after_timestamp and timestamp <= after_timestamp:
                    continue

                records.append({
                    'device_user_id': device_user_id,
                    'timestamp': timestamp,
                    'status': status
                })

            records.sort(key=lambda x: x['timestamp'])

            processed = 0
            skipped = 0
            errors = 0

            for record in records:
                try:
                    device_user_id = record['device_user_id']
                    timestamp = record['timestamp']

                    if not device_user_id or not timestamp:
                        skipped += 1
                        continue

                    employee = self.env['hr.employee'].search([
                        ('device_user_id', '=', str(device_user_id))
                    ], limit=1)

                    if not employee:
                        _logger.warning(f"No employee found for ID {device_user_id}")
                        skipped += 1
                        continue

                    # Convert timestamp from device timezone to UTC
                    device_tz = pytz.timezone(self.timezone)
                    # Make timestamp timezone-aware in device timezone
                    local_dt = device_tz.localize(timestamp)
                    # Convert to UTC
                    utc_dt = local_dt.astimezone(pytz.UTC)
                    # Remove timezone info for Odoo (Odoo stores as naive UTC)
                    timestamp_utc = utc_dt.replace(tzinfo=None)

                    # Check if this exact timestamp already exists as check_in OR check_out
                    existing_checkin = self.env['hr.attendance'].search([
                        ('employee_id', '=', employee.id),
                        ('check_in', '=', timestamp_utc.strftime('%Y-%m-%d %H:%M:%S'))
                    ], limit=1)
                    
                    existing_checkout = self.env['hr.attendance'].search([
                        ('employee_id', '=', employee.id),
                        ('check_out', '=', timestamp_utc.strftime('%Y-%m-%d %H:%M:%S'))
                    ], limit=1)

                    if existing_checkin or existing_checkout:
                        skipped += 1
                        _logger.debug(f"Skipped duplicate timestamp {timestamp_utc} for {employee.name}")
                        continue

                    # Find the last attendance record for this employee
                    last_attendance = self.env['hr.attendance'].search([
                        ('employee_id', '=', employee.id)
                    ], order='check_in desc', limit=1)

                    # Alternate logic: if last record has no check_out, update it; otherwise create new
                    if last_attendance and not last_attendance.check_out:
                        # This is a check-out
                        last_attendance.write({'check_out': timestamp_utc})
                        processed += 1
                        _logger.info(f"Check-out for {employee.name} at {timestamp_utc}")
                    else:
                        # This is a check-in (create new record)
                        self.env['hr.attendance'].create({
                            'employee_id': employee.id,
                            'check_in': timestamp_utc,
                        })
                        processed += 1
                        _logger.info(f"Check-in for {employee.name} at {timestamp_utc}")

                except Exception as e:
                    errors += 1
                    _logger.error(f"Error processing record: {e}")

            message = f"Sync result:\n- Processed: {processed}\n- Skipped: {skipped}\n- Errors: {errors}"

            sync_log.write({
                'state': 'success' if errors == 0 else 'warning',
                'message': message,
                'records_processed': processed,
            })

            self.write({
                'state': 'connected',
                'last_sync_time': fields.Datetime.now(),
            })

            self._disconnect_zk(conn)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            error_msg = str(e)
            sync_log.write({
                'state': 'error',
                'message': error_msg,
            })
            self.write({
                'state': 'error',
                'last_error': error_msg,
            })
            if conn:
                self._disconnect_zk(conn)
            raise UserError(_('Attendance sync failed: %s') % error_msg)

    def action_view_sync_logs(self):
        """View sync logs"""
        self.ensure_one()
        return {
            'name': _('Sync Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'zk.sync.log',
            'view_mode': 'list,form',
            'domain': [('device_id', '=', self.id)],
            'context': {'default_device_id': self.id},
        }

    @api.model
    def cron_sync_all_devices(self):
        """Cron job to sync all active devices"""
        devices = self.search([('active', '=', True)])
        for device in devices:
            try:
                if device.sync_users:
                    last_user_sync = device.last_user_sync_time or fields.Datetime.from_string('2000-01-01')
                    minutes_since_sync = (fields.Datetime.now() - last_user_sync).total_seconds() / 60
                    if minutes_since_sync >= device.sync_users_interval:
                        device._sync_users_to_device()
                if device.sync_attendance:
                    device._sync_attendance_from_device()
            except Exception as e:
                _logger.error(f"Error syncing device {device.name}: {e}")
                continue
#----------------------------------------------------------------


# # -*- coding: utf-8 -*-
# from odoo import models, fields, api, _
# from odoo.exceptions import UserError, ValidationError
# import logging
# from datetime import datetime, timedelta
# from zk import ZK
#
# _logger = logging.getLogger(__name__)
#
#
# class ZKDevice(models.Model):
#     _name = 'zk.device'
#     _description = 'جهاز البصمة ZK'
#     _inherit = ['mail.thread', 'mail.activity.mixin']   # ← أهم سطر
#     _order = 'name'
#
#     name = fields.Char('اسم الجهاز', required=True)
#     ip_address = fields.Char('عنوان IP', required=True)
#     port = fields.Integer('المنفذ', default=4370, required=True)
#     timeout = fields.Integer('المهلة الزمنية (ثانية)', default=5)
#
#     # إعدادات المزامنة
#     sync_users = fields.Boolean('مزامنة المستخدمين', default=True,
#                                 help='مزامنة موظفي Odoo إلى الجهاز')
#     sync_users_interval = fields.Integer('فترة مزامنة المستخدمين (دقيقة)', default=60)
#     sync_attendance = fields.Boolean('مزامنة الحضور', default=True)
#     sync_attendance_interval = fields.Integer('فترة مزامنة الحضور (ثانية)', default=10)
#
#     # حالة الاتصال
#     state = fields.Selection([
#         ('disconnected', 'غير متصل'),
#         ('connected', 'متصل'),
#         ('syncing', 'جاري المزامنة'),
#         ('error', 'خطأ')
#     ], string='الحالة', default='disconnected', readonly=True)
#
#     last_sync_time = fields.Datetime('آخر مزامنة', readonly=True)
#     last_user_sync_time = fields.Datetime('آخر مزامنة مستخدمين', readonly=True)
#     last_error = fields.Text('آخر خطأ', readonly=True)
#
#     # معلومات الجهاز
#     device_name = fields.Char('اسم الجهاز الفعلي', readonly=True)
#     serial_number = fields.Char('الرقم التسلسلي', readonly=True)
#     firmware_version = fields.Char('إصدار البرنامج الثابت', readonly=True)
#     total_users = fields.Integer('عدد المستخدمين', readonly=True)
#
#     # العلاقات
#     sync_log_ids = fields.One2many('zk.sync.log', 'device_id', string='سجلات المزامنة')
#     sync_log_count = fields.Integer('عدد السجلات', compute='_compute_sync_log_count')
#
#     # إعدادات الحالة
#     # checkin_status = fields.Integer('حالة تسجيل الدخول', default=0,
#     #                                 help='القيمة المستخدمة في الجهاز للدلالة على تسجيل الدخول')
#     # checkout_status = fields.Integer('حالة تسجيل الخروج', default=1,
#     #                                  help='القيمة المستخدمة في الجهاز للدلالة على تسجيل الخروج')
#
#     active = fields.Boolean('نشط', default=True)
#
#     @api.depends('sync_log_ids')
#     def _compute_sync_log_count(self):
#         for device in self:
#             device.sync_log_count = len(device.sync_log_ids)
#
#     @api.constrains('ip_address', 'port')
#     def _check_connection_params(self):
#         for device in self:
#             if not device.ip_address:
#                 raise ValidationError(_('عنوان IP مطلوب'))
#             if device.port <= 0 or device.port > 65535:
#                 raise ValidationError(_('رقم المنفذ يجب أن يكون بين 1 و 65535'))
#
#     def _get_zk_connection(self):
#         """إنشاء اتصال بجهاز ZK"""
#         self.ensure_one()
#         zk = ZK(self.ip_address, port=self.port, timeout=self.timeout)
#         try:
#             conn = zk.connect()
#             conn.disable_device()
#             return conn
#         except Exception as e:
#             _logger.error(f"فشل الاتصال بالجهاز {self.name}: {e}")
#             raise UserError(_('فشل الاتصال بجهاز البصمة: %s') % str(e))
#
#     def _disconnect_zk(self, conn):
#         """قطع الاتصال بجهاز ZK"""
#         try:
#             if conn:
#                 conn.enable_device()
#                 conn.disconnect()
#         except Exception as e:
#             _logger.warning(f"خطأ عند قطع الاتصال: {e}")
#
#     def action_test_connection(self):
#         """اختبار الاتصال بالجهاز"""
#         self.ensure_one()
#         conn = None
#         try:
#             conn = self._get_zk_connection()
#
#             # جلب معلومات الجهاز
#             try:
#                 device_name = conn.get_device_name() or 'Unknown'
#                 serial_number = conn.get_serialnumber() or 'Unknown'
#                 firmware = conn.get_firmware_version() or 'Unknown'
#                 users = conn.get_users()
#
#                 self.write({
#                     'state': 'connected',
#                     'device_name': device_name,
#                     'serial_number': serial_number,
#                     'firmware_version': firmware,
#                     'total_users': len(users),
#                     'last_error': False,
#                 })
#             except Exception:
#                 # بعض الأجهزة لا تدعم جميع الوظائف
#                 self.state = 'connected'
#
#             self._disconnect_zk(conn)
#
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'display_notification',
#                 'params': {
#                     'title': _('نجح الاتصال'),
#                     'message': _('تم الاتصال بالجهاز بنجاح'),
#                     'type': 'success',
#                     'sticky': False,
#                 }
#             }
#         except Exception as e:
#             self.write({
#                 'state': 'error',
#                 'last_error': str(e),
#             })
#             if conn:
#                 self._disconnect_zk(conn)
#             raise UserError(_('فشل الاتصال: %s') % str(e))
#
#     def action_sync_users(self):
#         """مزامنة المستخدمين من Odoo إلى الجهاز"""
#         self.ensure_one()
#         if not self.sync_users:
#             raise UserError(_('مزامنة المستخدمين غير مفعلة لهذا الجهاز'))
#
#         return self._sync_users_to_device()
#
#     def _sync_users_to_device(self):
#         """مزامنة المستخدمين الفعلية"""
#         self.ensure_one()
#         conn = None
#         sync_log = self.env['zk.sync.log'].create({
#             'device_id': self.id,
#             'sync_type': 'user',
#             'state': 'running',
#         })
#
#         try:
#             self.state = 'syncing'
#             conn = self._get_zk_connection()
#
#             # جلب موظفي Odoo الذين لديهم device_user_id
#             employees = self.env['hr.employee'].search([
#                 ('device_user_id', '!=', False)
#             ])
#
#             if not employees:
#                 sync_log.write({
#                     'state': 'warning',
#                     'message': 'لا يوجد موظفين لديهم device_user_id',
#                 })
#                 self.state = 'connected'
#                 self._disconnect_zk(conn)
#                 return
#
#             # جلب مستخدمي الجهاز الحاليين
#             device_users = conn.get_users()
#             device_user_dict = {
#                 (getattr(u, 'user_id', None) or getattr(u, 'uid', None)):
#                     (getattr(u, 'name', '') or getattr(u, 'username', ''))
#                 for u in device_users
#             }
#
#             created = 0
#             updated = 0
#             errors = 0
#
#             for emp in employees:
#                 try:
#                     device_id = int(emp.device_user_id)
#                     emp_name = emp.name[:24]  # حد الأحرف في أجهزة ZK
#
#                     if device_id in device_user_dict:
#                         # المستخدم موجود - تحقق من الاسم
#                         if device_user_dict[device_id] != emp_name:
#                             # حذف وإعادة إنشاء للتحديث
#                             conn.delete_user(uid=device_id)
#                             conn.set_user(
#                                 uid=device_id,
#                                 name=emp_name,
#                                 privilege=0,
#                                 password='',
#                                 group_id='',
#                                 user_id=str(device_id)
#                             )
#                             updated += 1
#                             _logger.info(f"تم تحديث المستخدم {device_id}: {emp_name}")
#                     else:
#                         # المستخدم غير موجود - أنشئه
#                         conn.set_user(
#                             uid=device_id,
#                             name=emp_name,
#                             privilege=0,
#                             password='',
#                             group_id='',
#                             user_id=str(device_id)
#                         )
#                         created += 1
#                         _logger.info(f"تم إنشاء المستخدم {device_id}: {emp_name}")
#
#                 except Exception as e:
#                     errors += 1
#                     _logger.error(f"خطأ في مزامنة الموظف {emp.name}: {e}")
#
#             message = f"تمت المزامنة بنجاح:\n"
#             message += f"- تم الإنشاء: {created}\n"
#             message += f"- تم التحديث: {updated}\n"
#             message += f"- أخطاء: {errors}"
#
#             sync_log.write({
#                 'state': 'success' if errors == 0 else 'warning',
#                 'message': message,
#                 'records_processed': created + updated,
#             })
#
#             self.write({
#                 'state': 'connected',
#                 'last_user_sync_time': fields.Datetime.now(),
#                 'total_users': len(device_users) + created,
#             })
#
#             self._disconnect_zk(conn)
#
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'display_notification',
#                 'params': {
#                     'title': _('نجحت المزامنة'),
#                     'message': message,
#                     'type': 'success',
#                     'sticky': False,
#                 }
#             }
#
#         except Exception as e:
#             error_msg = str(e)
#             sync_log.write({
#                 'state': 'error',
#                 'message': error_msg,
#             })
#             self.write({
#                 'state': 'error',
#                 'last_error': error_msg,
#             })
#             if conn:
#                 self._disconnect_zk(conn)
#             raise UserError(_('فشلت مزامنة المستخدمين: %s') % error_msg)
#
#     def action_sync_attendance(self):
#         """مزامنة سجلات الحضور من الجهاز"""
#         self.ensure_one()
#         if not self.sync_attendance:
#             raise UserError(_('مزامنة الحضور غير مفعلة لهذا الجهاز'))
#
#         return self._sync_attendance_from_device()
#
#     def _sync_attendance_from_device(self, after_timestamp=None):
#         """مزامنة سجلات الحضور الفعلية"""
#         self.ensure_one()
#         conn = None
#         sync_log = self.env['zk.sync.log'].create({
#             'device_id': self.id,
#             'sync_type': 'attendance',
#             'state': 'running',
#         })
#
#         try:
#             self.state = 'syncing'
#             conn = self._get_zk_connection()
#
#             # جلب سجلات الحضور
#             attendances = conn.get_attendance()
#
#             if not attendances:
#                 sync_log.write({
#                     'state': 'success',
#                     'message': 'لا توجد سجلات حضور جديدة',
#                 })
#                 self.state = 'connected'
#                 self._disconnect_zk(conn)
#                 return
#
#             # تحويل السجلات إلى قائمة
#             records = []
#             for att in attendances:
#                 device_user_id = getattr(att, 'user_id', None) or getattr(att, 'uid', None)
#                 timestamp = att.timestamp
#                 status = getattr(att, 'status', None)
#
#                 # تصفية حسب الوقت
#                 if after_timestamp and timestamp <= after_timestamp:
#                     continue
#
#                 records.append({
#                     'device_user_id': device_user_id,
#                     'timestamp': timestamp,
#                     'status': status
#                 })
#
#             # ترتيب حسب الوقت
#             records.sort(key=lambda x: x['timestamp'])
#
#             processed = 0
#             skipped = 0
#             errors = 0
#
#             for record in records:
#                 try:
#                     device_user_id = record['device_user_id']
#                     timestamp = record['timestamp']
#                     status = record['status']
#
#                     if not device_user_id or not timestamp:
#                         skipped += 1
#                         continue
#
#                     # البحث عن الموظف
#                     employee = self.env['hr.employee'].search([
#                         ('device_user_id', '=', str(device_user_id))
#                     ], limit=1)
#
#                     if not employee:
#                         _logger.warning(f"لا يوجد موظف للمعرف {device_user_id}")
#                         skipped += 1
#                         continue
#
#                     # التحقق من وجود السجل
#                     existing = self.env['hr.attendance'].search([
#                         ('employee_id', '=', employee.id),
#                         ('check_in', '=', timestamp.strftime('%Y-%m-%d %H:%M:%S'))
#                     ], limit=1)
#
#                     if existing:
#                         skipped += 1
#                         continue
#
#                     # معالجة السجل حسب الحالة
#                     if status == self.checkin_status:
#                         # تسجيل دخول
#                         self.env['hr.attendance'].create({
#                             'employee_id': employee.id,
#                             'check_in': timestamp,
#                         })
#                         processed += 1
#                     elif status == self.checkout_status:
#                         # تسجيل خروج
#                         open_attendance = self.env['hr.attendance'].search([
#                             ('employee_id', '=', employee.id),
#                             ('check_out', '=', False)
#                         ], order='check_in desc', limit=1)
#
#                         if open_attendance:
#                             open_attendance.check_out = timestamp
#                             processed += 1
#                         else:
#                             # إنشاء سجل مباشر
#                             self.env['hr.attendance'].create({
#                                 'employee_id': employee.id,
#                                 'check_in': timestamp,
#                                 'check_out': timestamp,
#                             })
#                             processed += 1
#                     else:
#                         # حالة غير معروفة - تسجيل دخول افتراضي
#                         self.env['hr.attendance'].create({
#                             'employee_id': employee.id,
#                             'check_in': timestamp,
#                         })
#                         processed += 1
#
#                 except Exception as e:
#                     errors += 1
#                     _logger.error(f"خطأ في معالجة السجل: {e}")
#
#             message = f"تمت المزامنة:\n"
#             message += f"- تمت المعالجة: {processed}\n"
#             message += f"- تم التجاهل: {skipped}\n"
#             message += f"- أخطاء: {errors}"
#
#             sync_log.write({
#                 'state': 'success' if errors == 0 else 'warning',
#                 'message': message,
#                 'records_processed': processed,
#             })
#
#             self.write({
#                 'state': 'connected',
#                 'last_sync_time': fields.Datetime.now(),
#             })
#
#             self._disconnect_zk(conn)
#
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'display_notification',
#                 'params': {
#                     'title': _('نجحت المزامنة'),
#                     'message': message,
#                     'type': 'success',
#                     'sticky': False,
#                 }
#             }
#
#         except Exception as e:
#             error_msg = str(e)
#             sync_log.write({
#                 'state': 'error',
#                 'message': error_msg,
#             })
#             self.write({
#                 'state': 'error',
#                 'last_error': error_msg,
#             })
#             if conn:
#                 self._disconnect_zk(conn)
#             raise UserError(_('فشلت مزامنة الحضور: %s') % error_msg)
#
#     def action_view_sync_logs(self):
#         """عرض سجلات المزامنة"""
#         self.ensure_one()
#         return {
#             'name': _('سجلات المزامنة'),
#             'type': 'ir.actions.act_window',
#             'res_model': 'zk.sync.log',
#             'view_mode': 'list,form',
#             'domain': [('device_id', '=', self.id)],
#             'context': {'default_device_id': self.id},
#         }
#
#     @api.model
#     def cron_sync_all_devices(self):
#         """Cron job لمزامنة جميع الأجهزة"""
#         devices = self.search([('active', '=', True)])
#         for device in devices:
#             try:
#                 # مزامنة المستخدمين
#                 if device.sync_users:
#                     last_user_sync = device.last_user_sync_time or fields.Datetime.from_string('2000-01-01')
#                     minutes_since_sync = (fields.Datetime.now() - last_user_sync).total_seconds() / 60
#                     if minutes_since_sync >= device.sync_users_interval:
#                         device._sync_users_to_device()
#
#                 # مزامنة الحضور
#                 if device.sync_attendance:
#                     device._sync_attendance_from_device()
#
#             except Exception as e:
#                 _logger.error(f"خطأ في مزامنة الجهاز {device.name}: {e}")
#                 continue
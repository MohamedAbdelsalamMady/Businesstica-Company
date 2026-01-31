from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging
import pytz

_logger = logging.getLogger(__name__)

try:
    from zk import ZK
except ImportError:
    _logger.error('pyzk library not installed. Install: pip install pyzk')
    ZK = None


class AttendanceDevice(models.Model):
    _name = 'attendance.device'
    _description = 'Attendance Device'
    _rec_name = 'name'

    name = fields.Char(string='Device Name', required=True, default='Main Device')
    ip_address = fields.Char(string='IP Address', required=True)
    port = fields.Integer(string='Port', default=4370, required=True)
    active = fields.Boolean(string='Active', default=True)
    auto_sync = fields.Boolean(string='Auto Sync', default=True)
    auto_fetch_attendance = fields.Boolean(string='Auto Fetch Attendance', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    last_fetch_date = fields.Datetime(string='Last Fetch Date', readonly=True)
    sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('syncing', 'Syncing'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Sync Status', default='not_synced')
    sync_log = fields.Text(string='Sync Log', readonly=True)
    timezone = fields.Selection(
        '_get_timezone_list',
        string='Timezone',
        default='Africa/Cairo',
        required=True,
        help='Device timezone for attendance records'
    )

    @api.model
    def _get_timezone_list(self):
        """Get list of timezones
        pytzهذه الدالة تقوم بأنشاء قائمة بكل المناطق الزمنية الموجودة في مكتبة
        """
        return [(tz, tz) for tz in pytz.all_timezones]

    def _connect_device(self):
        """Connect to biometric device دالة اتصال بجهاز البصمة
        هذه الدالة تحاول:
        التأكد من وجود مكتبة pyzk
        إنشاء اتصال بجهاز البصمة باستخدام الـ IP والـ Port
        تعطيل الجهاز مؤقتًا لمنع تدخل المستخدم أثناء نقل البيانات
        إرجاع الـ connection لاستخدامه في العمليات (جلب الحضور – مزامنة الموظفين)
        وإذا حدث أي خطأ → تُرجع رسالة واضحة للمستخدم وتكتب الخطأ في log.
        """
        if not ZK:
            raise UserError(_('pyzk library not installed. Install: pip install pyzk'))

        self.ensure_one()
        try:
            zk = ZK(self.ip_address, port=self.port, timeout=10, password=0, force_udp=False, ommit_ping=False)
            conn = zk.connect()
            conn.disable_device()
            return conn
        except Exception as e:
            _logger.error(f'Failed to connect to device {self.name}: {str(e)}')
            raise UserError(_('Connection failed: %s') % str(e))

    def sync_employees_to_device(self, employees=None):
        """Sync employees to device دالة إرسال الموظفين إلى جهاز البصمة
        🎯 الهدف من الدالة
        تحديد الموظفين المطلوب مزامنتهم
        الاتصال بجهاز البصمة
        إرسال أو تحديث بيانات كل موظف داخل الجهاز
        تسجيل نتائج المزامنة
        التعامل مع الأخطاء
        """
        self.ensure_one()

        if not employees:
            employees = self.env['hr.employee'].search([
                ('active', '=', True),
                ('device_user_id', '!=', False)
            ])

        if not employees:
            return False

        try:
            self.write({'sync_status': 'syncing'})
            conn = self._connect_device()

            device_users = conn.get_users()
            device_user_ids = {str(user.user_id): user for user in device_users}

            sync_log = []
            synced_count = 0

            for employee in employees:
                if not employee.device_user_id:
                    continue

                try:
                    user_id = int(employee.device_user_id)
                    name = employee.name or 'Unknown'

                    if employee.device_user_id in device_user_ids:
                        conn.set_user(
                            uid=user_id,
                            name=name,
                            privilege=0,
                            password='',
                            group_id='',
                            user_id=str(user_id)
                        )
                        sync_log.append(f'✓ Updated: {name} (ID: {user_id})')
                    else:
                        conn.set_user(
                            uid=user_id,
                            name=name,
                            privilege=0,
                            password='',
                            group_id='',
                            user_id=str(user_id)
                        )
                        sync_log.append(f'✓ Added: {name} (ID: {user_id})')

                    employee.write({
                        'synced_to_device': True,
                        'last_device_sync': fields.Datetime.now()
                    })
                    synced_count += 1

                except Exception as e:
                    sync_log.append(f'✗ Error for {employee.name}: {str(e)}')

            conn.enable_device()
            conn.disconnect()

            log_text = '\n'.join(sync_log)
            self.write({
                'sync_status': 'synced',
                'last_sync_date': fields.Datetime.now(),
                'sync_log': log_text
            })

            _logger.info(f'Synced {synced_count}/{len(employees)} employees to {self.name}')
            return True

        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_log': f'Sync failed: {str(e)}'
            })
            _logger.error(f'Sync failed: {str(e)}')
            return False

    def fetch_attendance_from_device(self):
        """Fetch attendance records from device
        الاتصال بجهاز البصمة
        قراءة جميع سجلات الحضور
        تحويل وقت الجهاز للـ UTC
        البحث عن الموظف المعني
        تحديد Check In أو Check Out بشكل تلقائي
        إنشاء سجلات الحضور داخل Odoo
        تسجيل المشاكل والأخطاء
        تحديث آخر وقت جلب
        """
        self.ensure_one()

        if not self.auto_fetch_attendance:
            return 0

        try:
            conn = self._connect_device()

            # Get all attendance records
            attendances = conn.get_attendance()

            conn.enable_device()
            conn.disconnect()

            if not attendances:
                return 0

            # Process attendance records
            created_count = 0
            device_tz = pytz.timezone(self.timezone)

            for att in attendances:
                try:
                    # Find employee by device_user_id
                    employee = self.env['hr.employee'].search([
                        ('device_user_id', '=', str(att.user_id))
                    ], limit=1)

                    if not employee:
                        continue

                    # Convert device time to UTC
                    device_time = device_tz.localize(att.timestamp)
                    utc_time = device_time.astimezone(pytz.UTC).replace(tzinfo=None)

                    # Check if record already exists
                    existing = self.env['hr.attendance'].search([
                        ('employee_id', '=', employee.id),
                        ('device_timestamp', '=', utc_time),
                        ('is_from_device', '=', True)
                    ], limit=1)

                    if existing:
                        continue

                    # Determine check in or check out
                    last_attendance = self.env['hr.attendance'].search([
                        ('employee_id', '=', employee.id)
                    ], order='check_in desc', limit=1)

                    # Create attendance record
                    if not last_attendance or last_attendance.check_out:
                        # Check in
                        self.env['hr.attendance'].create({
                            'employee_id': employee.id,
                            'check_in': utc_time,
                            'device_id': self.id,
                            'device_timestamp': utc_time,
                            'is_from_device': True
                        })
                        created_count += 1
                    else:
                        # Check out
                        last_attendance.write({
                            'check_out': utc_time,
                            'device_id': self.id,
                            'is_from_device': True
                        })
                        created_count += 1

                except Exception as e:
                    _logger.error(f'Error processing attendance: {str(e)}')
                    continue

            self.write({'last_fetch_date': fields.Datetime.now()})

            if created_count > 0:
                _logger.info(f'Created {created_count} attendance records from {self.name}')

            return created_count

        except Exception as e:
            _logger.error(f'Failed to fetch attendance from {self.name}: {str(e)}')
            return 0

    @api.model
    def cron_auto_sync_employees(self):
        """Scheduled: Sync employees to devices every hour"""
        devices = self.search([('active', '=', True), ('auto_sync', '=', True)])

        for device in devices:
            try:
                self.env['hr.employee'].ensure_all_have_device_ids()
                device.sync_employees_to_device()
            except Exception as e:
                _logger.error(f'Auto sync failed for {device.name}: {str(e)}')

    @api.model
    def cron_auto_fetch_attendance(self): # هذه الدالة الذي يستدعيها الكرون جوب عشان تبحث على الريكوردات الي متوصلة بجهاز البصمة
        """Scheduled: Fetch attendance every 5 seconds"""
        devices = self.search([
            ('active', '=', True),
            ('auto_fetch_attendance', '=', True)
        ])

        for device in devices:
            try:
                device.fetch_attendance_from_device() # ثم تستدعي الدالة المخصصة بجلب الحضور من البصمة
            except Exception as e:
                _logger.error(f'Auto fetch failed for {device.name}: {str(e)}')


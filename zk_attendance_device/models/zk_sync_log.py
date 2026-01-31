# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ZKSyncLog(models.Model):
    _name = 'zk.sync.log'
    _description = 'ZK Sync Log'
    _order = 'create_date desc'
    _rec_name = 'device_id'

    # Related device
    device_id = fields.Many2one('zk.device', string='Device', required=True, ondelete='cascade')

    # Sync type
    sync_type = fields.Selection([
        ('user', 'User Sync'),
        ('attendance', 'Attendance Sync'),
    ], string='Sync Type', required=True)

    # Status
    state = fields.Selection([
        ('running', 'Running'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ], string='State', default='running', required=True)

    message = fields.Text('Message')
    records_processed = fields.Integer('Records Processed', default=0)

    create_date = fields.Datetime('Creation Date', readonly=True)

    def name_get(self):
        """Display name for the record: Device - Sync Type - Date"""
        result = []
        for record in self:
            sync_type_dict = dict(self._fields['sync_type'].selection)
            name = f"{record.device_id.name} - {sync_type_dict.get(record.sync_type)} - {record.create_date}"
            result.append((record.id, name))
        return result
#--------------------------------------------------------------
# -*- coding: utf-8 -*-
# from odoo import models, fields, api
#
#
# class ZKSyncLog(models.Model):
#     _name = 'zk.sync.log'
#     _description = 'سجل مزامنة ZK'
#     _order = 'create_date desc'
#     _rec_name = 'device_id'
#
#     device_id = fields.Many2one('zk.device', string='الجهاز', required=True, ondelete='cascade')
#     sync_type = fields.Selection([
#         ('user', 'مزامنة مستخدمين'),
#         ('attendance', 'مزامنة حضور'),
#     ], string='نوع المزامنة', required=True)
#
#     state = fields.Selection([
#         ('running', 'جاري التنفيذ'),
#         ('success', 'نجح'),
#         ('warning', 'تحذير'),
#         ('error', 'خطأ'),
#     ], string='الحالة', default='running', required=True)
#
#     message = fields.Text('الرسالة')
#     records_processed = fields.Integer('عدد السجلات المعالجة', default=0)
#
#     create_date = fields.Datetime('تاريخ الإنشاء', readonly=True)
#
#     def name_get(self):
#         result = []
#         for record in self:
#             sync_type_dict = dict(self._fields['sync_type'].selection)
#             name = f"{record.device_id.name} - {sync_type_dict.get(record.sync_type)} - {record.create_date}"
#             result.append((record.id, name))
#         return result
{
    'name': "ZK Attendance Device",
    'author': "Mohamed Ramadan",
    'version': '18.0.0.1.0',
    'depends': ['base', 'hr', 'hr_attendance'],
    'external_dependencies': {
        'python': ['zk'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/zk_device_views.xml',
        'views/zk_sync_log_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/menu_views.xml',
        'data/ir_cron_data.xml',
    ],
    # 'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}


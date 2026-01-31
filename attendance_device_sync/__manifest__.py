{
    'name': "Attendance Device Sync",
    'author': "Mohamed Ramadan",
    'version': '18.0.0.1.0',
    'depends': ['base', 'hr', 'hr_attendance'],
    'external_dependencies': {
        'python': ['zk'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/default_device.xml',
        'views/attendance_device_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}


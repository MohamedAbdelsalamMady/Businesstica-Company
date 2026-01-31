from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    """Run after module installation"""
    # Generate device_user_id for all employees
    employees = env['hr.employee'].search([
        ('device_user_id', '=', False),
        ('active', '=', True)
    ])

    for employee in employees:
        employee.device_user_id = env['hr.employee']._generate_device_user_id()

    # Activate auto-sync for all devices
    devices = env['attendance.device'].search([])
    devices.write({'auto_sync': True, 'active': True})

    # Start initial sync
    if devices:
        devices[0].sync_employees_to_device()
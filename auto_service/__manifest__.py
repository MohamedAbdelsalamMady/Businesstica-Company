# -*- coding: utf-8 -*-
{
    'name': "auto_service",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in the module listing.
    # Check https://github.com/odoo/odoo/blob/18.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list.
    'category': 'Services/Auto Repair',
    'version': '18.0.1.0.0',  # Updated to match Odoo 18

    # Update dependencies to match Odoo 18 module structure
    'depends': [
        'base',
        'sale_management',  # Replaces 'sale'
        'product',
        'project',
        'account',
        'stock',
        'purchase',
        'purchase_requisition',
        'sale_stock',
        'mrp',
    ],

    # Data files always loaded
    'data': [
        'data/demo_data.xml',
        'security/reception_groups.xml',
        'security/ir.model.access.csv',
        'wizard/purchase_requisition.xml',
        'wizard/send_to_pricing.xml',
        'wizard/warning.xml',
        'wizard/new_diagnoses_items_wizard.xml',
        'views/views.xml',
        'views/car_agent.xml',
        'views/car_body_style.xml',
        'views/car_brand.xml',
        'views/car_creations.xml',
        'views/car_cylinders.xml',
        'views/car_generation.xml',
        'views/car_model.xml',
        'views/car_origin.xml',
        'views/engine_capacity.xml',
        'views/engine_type.xml',
        'views/reception_information.xml',
        'views/service_name.xml',
        'views/service_team.xml',
        'views/service_type.xml',
        'views/transmission_type.xml',
        'views/task_location.xml',
        'views/car_diagnoses.xml',
        'views/sale_order.xml',
        'views/project_task.xml',
        'views/account_move.xml',
        'views/stock_move.xml',
        'views/stock_picking.xml',
        'views/project_project.xml',
        'views/wait_to_deliver.xml',
        'views/purchase_order.xml',
        'views/pricing.xml',
        'views/pre_travel_vehicle_inspection.xml',
        'views/res_config_settings_view.xml',
        'views/report_plumbing_workshop.xml',
        'views/report_workshop_mechanics.xml',
        'views/inspection_transfer_ownership.xml',
        'views/res_company.xml',
        'report/pre_travel_pehicle_inspection_report.xml',
        'report/pre_travel_vehicle_inspection_template.xml',
        'report/inspection_transfer_ownership_report.xml',
        'report/inspection_transfer_ownership_template.xml',
        'report/plumbing_workshop_report.xml',
        'report/plumbing_workshop_template.xml',
        'report/workshop_mechanics_report.xml',
        'report/workshop_mechanics_template.xml',
        'report/wait_to_deliver_report.xml',
        'report/wait_to_deliver_report_template.xml',
        'report/account_move_diagnoses.xml',
        'report/account_move_diagnoses_template.xml',
        'report/car_diagnoses_report.xml',
        'report/car_diagnoses_template.xml',
        'report/reception_information_report.xml',
        'report/reception_information_template.xml',
        'views/menus.xml',
    ],

    # Demo data files loaded in demonstration mode only
    'demo': [
        'demo/demo.xml',
    ],

    # Compatibility flags
    'application': True,  # Indicates it's an application
    'installable': True,
    'auto_install': False,
}

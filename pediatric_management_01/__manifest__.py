# -*- coding: utf-8 -*-
{
    'name': 'Pediatric Practice Management',
    'version': '18.0.1.0.2',
    'category': 'Healthcare',
    'summary': 'Comprehensive management solution for pediatric clinics',
    'description': """
        A complete management solution for pediatric practices including:
        - Patient management with detailed parent/guardian information
        - Smart appointment scheduling and planning
        - Clinical consultations with specialized medical examinations
        - Medical prescriptions with automatic dosage calculation based on weight
        - Billing and integrated payment management
        - Automated vaccination tracking and schedule
        - Pediatric growth charts (Weight/Height/Head Circumference)
        - Interactive dashboard with clinical and financial statistics
        - Fully customizable clinic configuration
        - Automatic alerts and patient notifications
        - Detailed medical and administrative reports
    """,
    'author': 'mrseigneur-stack',
    'website': 'https://github.com/mrseigneur-stack/pediatric_management',
    'license': 'AGPL-3',  # Changé en OPL-1 pour une compatibilité totale avec l'Odoo App Store
    'depends': [
        'base',
        'mail',
        'calendar',
        'account',
        'contacts',
        'web',
        'report_xlsx'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/pediatric_security.xml',
        
        # Base Data
        'data/ir_sequence_data.xml',
        'data/pediatric_medication_data.xml',
        'data/pediatric_vaccine_data.xml',
        'data/pediatric_config_data.xml',
        'data/pediatric_cron_data.xml',
        
        # Views
        'views/pediatric_growth_views.xml',
        'views/pediatric_patient_views.xml',
        'views/pediatric_appointment_views.xml',
        'views/pediatric_consultation_views.xml',
        'views/pediatric_prescription_views.xml',
        'views/pediatric_vaccination_views.xml',
        'views/pediatric_medication_views.xml',
        'views/pediatric_config_views.xml',
        'views/pediatric_dashboard_views.xml',
        'views/pediatric_menus.xml',
        
        # Reports
        'reports/pediatric_prescription_report.xml',
        'reports/pediatric_patient_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pediatric_management/static/src/css/pediatric_dashboard.css',
            'pediatric_management/static/src/js/pediatric_dashboard.js',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/icon.png'],
    'price': 0,
    'currency': 'EUR',
}
{
    'name': 'RFID Inventory Sync',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Synchronize and compare Odoo inventory with RFID system',
    'description': """
        RFID Inventory Sync
        ===================
        This application allows you to:
        * Track inventory using RFID data
        * Compare Odoo On-Hand quantity with RFID quantity
        * Calculate differences automatically
        * Integrate with external RFID systems via API
    """,
    'author': 'Your Company',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/rfid_sync_data.xml',
        'views/rfid_sync_views.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}

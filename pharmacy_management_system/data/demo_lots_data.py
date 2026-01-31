# -- coding: utf-8 --

##############################################################################
#                                                                            #
# Part of WebbyCrown Solutions (Website: www.webbycrown.com).                #
# Copyright © 2025 WebbyCrown Solutions. All Rights Reserved.                #
#                                                                            #
# This module is developed and maintained by WebbyCrown Solutions.           #
# Unauthorized copying of this file, via any medium, is strictly prohibited. #
# Licensed under the terms of the WebbyCrown Solutions License Agreement.    #
#                                                                            #
##############################################################################

import datetime
from odoo import api, SUPERUSER_ID


def _create_expiring_lots(env):
    """Create expiring stock lots for demo data."""
    StockLot = env['stock.lot']
    
    # Helper to get product variant from template XML ID
    def get_product_variant(template_xmlid):
        try:
            template = env.ref(f'pharmacy_management_system.{template_xmlid}', raise_if_not_found=False)
            if template:
                variant = env['product.product'].search([('product_tmpl_id', '=', template.id)], limit=1)
                return variant.id if variant else False
        except Exception:
            pass
        return False
    
    # Helper to get reference
    def get_ref(xmlid):
        try:
            return env.ref(f'pharmacy_management_system.{xmlid}', raise_if_not_found=False)
        except Exception:
            return False
    
    today = datetime.date.today()
    
    # Expiring lots data: (lot_name, product_template_xmlid, days_until_expiry, hospital_xmlid, pharmacy_xmlid)
    lots_data = [
        ('LOT-PARA-2025-001', 'product_template_paracetamol', 15, 'hospital_general', 'pharmacy_general_a'),
        ('LOT-PARA-2025-002', 'product_template_paracetamol', 25, 'hospital_city', 'pharmacy_city_main'),
        ('LOT-PARA-2025-003', 'product_template_paracetamol', 30, 'hospital_greenvalley', 'pharmacy_greenvalley_d'),
        ('LOT-AMOX-2025-001', 'product_template_amoxicillin', 10, 'hospital_sunrise', 'pharmacy_sunrise_east'),
        ('LOT-AMOX-2025-002', 'product_template_amoxicillin', 20, 'hospital_riverside', 'pharmacy_riverside_north'),
        ('LOT-AMOX-2025-003', 'product_template_amoxicillin', 3, 'hospital_memorial', 'pharmacy_memorial_n'),
        ('LOT-IBUP-2025-001', 'product_template_ibuprofen', 7, 'hospital_greenvalley', 'pharmacy_greenvalley_d'),
        ('LOT-IBUP-2025-002', 'product_template_ibuprofen', 28, 'hospital_memorial', 'pharmacy_memorial_n'),
        ('LOT-CETI-2025-001', 'product_template_cetirizine', 12, 'hospital_general', 'pharmacy_general_b'),
        ('LOT-CETI-2025-002', 'product_template_cetirizine', 22, 'hospital_city', 'pharmacy_city_south'),
        ('LOT-ACET-2025-001', 'product_template_acetaminophen', 5, 'hospital_sunrise', 'pharmacy_sunrise_west'),
        ('LOT-ACET-2025-002', 'product_template_acetaminophen', 18, 'hospital_riverside', 'pharmacy_riverside_south'),
    ]
    
    created_count = 0
    for lot_name, product_xmlid, days, hospital_xmlid, pharmacy_xmlid in lots_data:
        product_id = get_product_variant(product_xmlid)
        if not product_id:
            continue
        
        hospital = get_ref(hospital_xmlid)
        pharmacy = get_ref(pharmacy_xmlid)
        
        if not hospital or not pharmacy:
            continue
        
        expiry_date = today + datetime.timedelta(days=days)
        
        # Check if lot already exists
        existing = StockLot.search([
            ('name', '=', lot_name),
            ('product_id', '=', product_id)
        ], limit=1)
        
        if not existing:
            try:
                StockLot.create({
                    'name': lot_name,
                    'product_id': product_id,
                    'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                    'hospital_id': hospital.id,
                    'pharmacy_id': pharmacy.id,
                })
                created_count += 1
            except Exception:
                pass
    
    return created_count





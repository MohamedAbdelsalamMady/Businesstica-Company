import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class RfidInventorySync(models.Model):
    _name = 'rfid.inventory.sync'
    _description = 'RFID Inventory Synchronization'
    _rec_name = 'product_id'

    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        domain="[('usage', '=', 'internal')]",
        help="Physical location of the product"
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        help="Product to track"
    )

    on_hand_quantity = fields.Float(
        string='On Hand Quantity',
        compute='_compute_on_hand_quantity',
        store=True,
        readonly=True,
        help="Quantity currently in Odoo stock (Quantity - Reserved)"
    )

    rfid_quantity = fields.Float(
        string='RFID Quantity',
        default=0.0,
        help="Quantity received from RFID system"
    )

    difference = fields.Float(
        string='Difference',
        compute='_compute_difference',
        store=True,
        readonly=True,
        help="Difference = RFID Quantity - On Hand Quantity"
    )

    @api.depends('product_id', 'location_id')
    def _compute_on_hand_quantity(self):
        """
        Compute on_hand_quantity based on stock.quant.
        Triggered when Product or Location is selected.
        Formula: quantity - reserved_quantity
        """
        if not self:
            return

        # Optimization: Use _read_group to fetch sums in bulk (Odoo 18 style)
        # Use sudo() to ensure we read all quants regardless of user rules
        domain = [
            ('product_id', 'in', self.product_id.ids),
            ('location_id', 'in', self.location_id.ids),
            ('location_id.usage', '=', 'internal')
        ]
        
        # Fetch grouped data using modern API
        # Returns list of tuples: (product, location, quantity, reserved_quantity)
        groups = self.env['stock.quant'].sudo()._read_group(
            domain,
            groupby=['product_id', 'location_id'],
            aggregates=['quantity:sum', 'reserved_quantity:sum']
        )
        
        # Create lookup dictionary: (product_id, location_id) -> available_qty
        qty_map = {}
        for product, location, quantity, reserved_quantity in groups:
            available = (quantity or 0.0) - (reserved_quantity or 0.0)
            qty_map[(product.id, location.id)] = available
            
        for record in self:
            record.on_hand_quantity = qty_map.get((record.product_id.id, record.location_id.id), 0.0)

    @api.depends('rfid_quantity', 'on_hand_quantity')
    def _compute_difference(self):
        """
        Compute difference automatically.
        Difference = RFID Quantity - On Hand Quantity
        """
        for record in self:
            record.difference = record.rfid_quantity - record.on_hand_quantity

    @api.model
    def action_populate_inventory(self):
        """
        Sync all internal stock quants to this module.
        Only creates missing records.
        Quantity calculation is handled by compute method.
        """
        # Get all internal locations
        internal_locations = self.env['stock.location'].search([('usage', '=', 'internal')])
        
        # Get all quants in internal locations (Use sudo to ensure we get everything)
        quants = self.env['stock.quant'].sudo().search([
            ('location_id', 'in', internal_locations.ids)
        ])
        
        # Create dictionary for fast lookup
        existing = {
            (r.product_id.id, r.location_id.id): r 
            for r in self.search([])
        }
        
        vals_list = []
        # Use a set to avoid duplicates in the same batch
        seen_keys = set()
        
        for quant in quants:
            key = (quant.product_id.id, quant.location_id.id)
            if key not in existing and key not in seen_keys:
                # Create new record ONLY
                # No need to set on_hand_quantity, it will be computed
                vals_list.append({
                    'product_id': quant.product_id.id,
                    'location_id': quant.location_id.id,
                    'rfid_quantity': 0.0,
                })
                seen_keys.add(key)
        
        if vals_list:
            self.create(vals_list)
            
        # Force recompute of on_hand_quantity for all records
        # This ensures that changes in Odoo stock are reflected here
        # even for existing records.
        all_records = self.search([])
        all_records._compute_on_hand_quantity()
            
        return True



from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class WarningReception(models.TransientModel):
    """ Warning Reception """
    _name = 'warning.reception'
    _description = 'Warning Reception'

    yy = fields.Char(string="Warning Message")  # Just an example field

    def run_all_reception(self):
        """ Run All Reception """
        active_id = self._context.get('active_id')
        
        if not active_id:
            raise UserError(_("No active record found!"))
        
        # Browse the reception.information record
        reception = self.env['reception.information'].browse(active_id)

        if not reception:
            raise UserError(_("Reception record not found!"))

        try:
            # Call the test_dead method on the reception record
            reception.test_dead()
        except Exception as e:
            raise UserError(_("An error occurred while running the reception: %s" % str(e)))

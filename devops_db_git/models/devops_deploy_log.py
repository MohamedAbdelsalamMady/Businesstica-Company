from odoo import api, fields, models


class DevopsDeployLog(models.Model):
    _name = "devops.deploy.log"
    _description = "DevOps Deployment Log"
    _order = "datetime desc, id desc"

    project_id = fields.Many2one("devops.project", required=True, ondelete="cascade")
    database_name = fields.Char(required=True, readonly=True, index=True)
    operation = fields.Selection(
        selection=[("pull", "Pull"), ("push", "Push"), ("deploy", "Deploy")],
        required=True,
    )
    result = fields.Selection(selection=[("success", "Success"), ("failed", "Failed")], required=True)
    logs = fields.Text(required=True)
    datetime = fields.Datetime(required=True, default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("database_name"):
                vals["database_name"] = self.env.cr.dbname
        return super().create(vals_list)

import base64
import logging
from cryptography.fernet import Fernet, InvalidToken

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class DevopsProject(models.Model):
    _name = "devops.project"
    _description = "DevOps Project"
    _rec_name = "name"

    name = fields.Char(required=True)
    database_name = fields.Char(required=True, readonly=True, default=lambda self: self.env.cr.dbname, index=True)
    repository_url = fields.Char(required=True)
    branch = fields.Char(default="main", required=True)
    addons_path = fields.Char(required=True)
    auto_pull = fields.Boolean(default=False)
    auto_upgrade = fields.Boolean(default=True)
    last_pull = fields.Datetime(readonly=True)
    status = fields.Selection(
        selection=[("draft", "Draft"), ("ready", "Ready"), ("error", "Error")],
        default="draft",
        readonly=True,
    )
    active = fields.Boolean(default=True)
    git_token = fields.Char(string="Git Token", copy=False, password=True)
    encrypted_git_token = fields.Char(copy=False, groups="devops_db_git.group_devops_admin")
    deploy_log_ids = fields.One2many("devops.deploy.log", "project_id", string="Deployment Logs", readonly=True)

    _sql_constraints = [
        ("project_db_unique", "unique(database_name)", "Only one DevOps project can exist per database."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["database_name"] = self.env.cr.dbname
            token = vals.pop("git_token", False)
            if token:
                vals["encrypted_git_token"] = self._encrypt_token(token)
        return super().create(vals_list)

    def write(self, vals):
        if "database_name" in vals and any(record.database_name != self.env.cr.dbname for record in self):
            raise AccessError(_("Cross-database write operation is not allowed."))
        token = vals.pop("git_token", None)
        if token is not None:
            vals["encrypted_git_token"] = self._encrypt_token(token) if token else False
        return super().write(vals)

    @api.constrains("addons_path")
    def _check_addons_path(self):
        for rec in self:
            if rec.addons_path:
                self.env["devops.git.service"]._validate_addons_path(rec.addons_path)

    @api.onchange("addons_path")
    def _onchange_addons_path(self):
        if self.addons_path:
            self.addons_path = self.env["devops.git.service"]._validate_addons_path(self.addons_path)

    @api.constrains("database_name")
    def _check_database_name(self):
        for rec in self:
            if rec.database_name != self.env.cr.dbname:
                raise ValidationError(_("Project must remain bound to the current database only."))

    @property
    def git_token_decrypted(self):
        self.ensure_one()
        if not self.encrypted_git_token:
            return False
        return self._decrypt_token(self.encrypted_git_token)

    @api.model
    def _get_fernet(self):
        key = self.env["ir.config_parameter"].sudo().get_param("devops_db_git.fernet_key")
        if not key:
            key = Fernet.generate_key().decode()
            self.env["ir.config_parameter"].sudo().set_param("devops_db_git.fernet_key", key)
        return Fernet(key.encode())

    @api.model
    def _encrypt_token(self, value):
        if not value:
            return False
        encrypted = self._get_fernet().encrypt(value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    @api.model
    def _decrypt_token(self, value):
        try:
            encrypted = base64.b64decode(value)
            decrypted = self._get_fernet().decrypt(encrypted)
            return decrypted.decode("utf-8")
        except (InvalidToken, ValueError) as exc:
            _logger.exception("Token decryption failed: %s", exc)
            raise ValidationError(_("Stored git token is invalid. Please re-enter it.")) from exc

    def action_validate_project(self):
        self.ensure_one()
        self._ensure_current_database()
        ok, msg = self.env["devops.git.service"].check_repo(self)
        self.status = "ready" if ok else "error"
        self._create_log("deploy", "success" if ok else "failed", msg)

    def action_pull(self):
        self.ensure_one()
        self._ensure_current_database()
        result = self.env["devops.git.service"].pull(self)
        self.write({"last_pull": fields.Datetime.now(), "status": "ready"})
        self._create_log("pull", "success", result)

    def action_push(self):
        self.ensure_one()
        self._ensure_current_database()
        result = self.env["devops.git.service"].push(self)
        self._create_log("push", "success", result)

    def action_checkout_branch(self):
        self.ensure_one()
        self._ensure_current_database()
        result = self.env["devops.git.service"].checkout_branch(self, self.branch)
        self._create_log("deploy", "success", result)

    def _ensure_current_database(self):
        for rec in self:
            if rec.database_name != self.env.cr.dbname:
                raise AccessError(_("Cross-database operation is blocked for safety."))

    def _create_log(self, operation, result, logs):
        self.ensure_one()
        self.env["devops.deploy.log"].create(
            {
                "project_id": self.id,
                "database_name": self.env.cr.dbname,
                "operation": operation,
                "result": result,
                "logs": logs,
                "datetime": fields.Datetime.now(),
            }
        )

    def _auto_upgrade_modules(self, module_names):
        if not self.auto_upgrade:
            return
        module_model = self.env["ir.module.module"].sudo()
        modules = module_model.search(
            [
                ("name", "in", list(module_names)),
                ("state", "=", "installed"),
            ]
        )
        for mod in modules:
            mod.button_immediate_upgrade()

    @api.model
    def cron_auto_pull(self):
        projects = self.search(
            [
                ("database_name", "=", self.env.cr.dbname),
                ("auto_pull", "=", True),
                ("active", "=", True),
            ]
        )
        for project in projects:
            try:
                project.action_pull()
            except Exception as exc:  # pylint: disable=broad-except
                project.status = "error"
                project._create_log("pull", "failed", str(exc))

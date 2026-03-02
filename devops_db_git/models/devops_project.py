import base64
import logging
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DevopsProject(models.Model):
    _name = "devops.project"
    _description = "DevOps Project"
    _rec_name = "name"

    @api.model
    def _selection_databases(self):
        self.env.cr.execute(
            """
            SELECT datname
            FROM pg_database
            WHERE datistemplate = false
            ORDER BY datname
            """
        )
        return [(row[0], row[0]) for row in self.env.cr.fetchall()]

    name = fields.Char(required=True)
    database_name = fields.Selection(selection=_selection_databases, required=True, default=lambda self: self.env.cr.dbname)
    repository_url = fields.Char(required=True)
    branch = fields.Char(default="main", required=True)
    branch_ids = fields.One2many("devops.project.branch", "project_id", string="Remote Branches", readonly=True)
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
    repo_path = fields.Char(compute="_compute_repo_path", readonly=True)
    deploy_log_ids = fields.One2many("devops.deploy.log", "project_id", string="Deployment Logs", readonly=True)

    _sql_constraints = [
        ("project_db_unique", "unique(database_name)", "Only one DevOps project can exist per database."),
    ]

    @api.depends("database_name")
    def _compute_repo_path(self):
        base = self.env["ir.config_parameter"].sudo().get_param(
            "devops_db_git.repositories_base_path", "/mnt/extra-addons/devops_projects"
        )
        for rec in self:
            rec.repo_path = str(Path(base).expanduser() / (rec.database_name or "unknown_db"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = vals.pop("git_token", False)
            if token:
                vals["encrypted_git_token"] = self._encrypt_token(token)
        return super().create(vals_list)

    def write(self, vals):
        token = vals.pop("git_token", None)
        if token is not None:
            vals["encrypted_git_token"] = self._encrypt_token(token) if token else False
        return super().write(vals)

    @api.constrains("repository_url")
    def _check_repository_url(self):
        for rec in self:
            if not rec.repository_url.startswith(("http://", "https://", "git@")):
                raise ValidationError(_("Repository URL must start with http(s):// or git@"))

    @api.onchange("repository_url", "git_token")
    def _onchange_repository_url(self):
        if self.repository_url:
            self._fetch_branches(store=False)

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

    def _fetch_branches(self, store=True):
        self.ensure_one()
        branches = self.env["devops.git.service"].fetch_remote_branches(self.repository_url, self.git_token_decrypted)
        if store and self.id:
            self.branch_ids.unlink()
            self.branch_ids = [(0, 0, {"name": b}) for b in branches]
        if branches and (not self.branch or self.branch not in branches):
            self.branch = branches[0]
        return branches

    def action_fetch_branches(self):
        self.ensure_one()
        self._fetch_branches(store=True)

    def action_validate_project(self):
        self.ensure_one()
        ok, msg = self.env["devops.git.service"].check_repo(self)
        self.status = "ready" if ok else "error"
        self._create_log("deploy", "success" if ok else "failed", msg)

    def action_pull(self):
        self.ensure_one()
        result = self.env["devops.git.service"].pull(self)
        self.write({"last_pull": fields.Datetime.now(), "status": "ready"})
        self._create_log("pull", "success", result)

    def action_push(self):
        self.ensure_one()
        result = self.env["devops.git.service"].push(self)
        self._create_log("push", "success", result)

    def action_checkout_branch(self):
        self.ensure_one()
        result = self.env["devops.git.service"].checkout_branch(self, self.branch)
        self._create_log("deploy", "success", result)

    def _create_log(self, operation, result, logs):
        self.ensure_one()
        self.env["devops.deploy.log"].create(
            {
                "project_id": self.id,
                "database_name": self.database_name,
                "operation": operation,
                "result": result,
                "logs": logs,
                "datetime": fields.Datetime.now(),
            }
        )

    def _auto_upgrade_modules(self, module_names):
        if not self.auto_upgrade:
            return
        if self.database_name != self.env.cr.dbname:
            raise UserError(
                _(
                    "Auto-upgrade can only run when you are connected to the same database as the project. "
                    "Open database '%s' then run Pull again."
                )
                % self.database_name
            )
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
        projects = self.search([("auto_pull", "=", True), ("active", "=", True)])
        for project in projects:
            try:
                project.action_pull()
            except Exception as exc:  # pylint: disable=broad-except
                project.status = "error"
                project._create_log("pull", "failed", str(exc))


class DevopsProjectBranch(models.Model):
    _name = "devops.project.branch"
    _description = "DevOps Project Branch"
    _order = "name"

    project_id = fields.Many2one("devops.project", required=True, ondelete="cascade")
    name = fields.Char(required=True)

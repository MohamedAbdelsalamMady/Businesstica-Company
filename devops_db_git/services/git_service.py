import logging
import os
import shlex
import subprocess
from pathlib import Path

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DevopsGitService(models.AbstractModel):
    _name = "devops.git.service"
    _description = "DevOps Git Service"

    def _validate_addons_path(self, path):
        normalized = Path(path).expanduser().resolve()
        if not normalized.exists():
            raise UserError(_("Addons path does not exist: %s") % normalized)
        if not normalized.is_dir():
            raise UserError(_("Addons path must be a directory: %s") % normalized)
        return str(normalized)

    def _build_env(self, project):
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        token = project.git_token_decrypted
        if token:
            env["GIT_ASKPASS"] = "echo"
            env["GIT_HTTP_PASSWORD"] = token
        return env

    def _run_git(self, project, args):
        path = self._validate_addons_path(project.addons_path)
        if not (Path(path) / ".git").exists():
            raise UserError(_("Path is not a git repository: %s") % path)

        cmd = ["git", *args]
        _logger.info("Running git command on %s@%s: %s", project.display_name, project.database_name, shlex.join(cmd))

        process = subprocess.run(
            cmd,
            cwd=path,
            env=self._build_env(project),
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        output = "\n".join(filter(None, [process.stdout, process.stderr]))
        if process.returncode:
            raise UserError(_("Git command failed (%s):\n%s") % (shlex.join(cmd), output))
        return output or _("Command executed successfully.")

    def check_repo(self, project):
        path = self._validate_addons_path(project.addons_path)
        git_dir = Path(path) / ".git"
        if not git_dir.exists():
            return False, _("No git repository found at addons path.")

        output = self._run_git(project, ["remote", "get-url", "origin"])
        if project.repository_url and project.repository_url.strip() not in output.strip():
            return False, _("Repository URL mismatch. Expected %(expected)s and got %(actual)s") % {
                "expected": project.repository_url,
                "actual": output.strip(),
            }
        return True, _("Repository is configured correctly.")

    def pull(self, project):
        self._run_git(project, ["fetch", "origin"])
        result = self._run_git(project, ["pull", "origin", project.branch])
        changed_modules = self._collect_changed_modules(project)
        if changed_modules:
            project._auto_upgrade_modules(changed_modules)
            result = "%s\n\n%s\n%s" % (
                result,
                _("Auto-upgraded modules:"),
                ", ".join(sorted(changed_modules)),
            )
        return result

    def push(self, project):
        return self._run_git(project, ["push", "origin", project.branch])

    def checkout_branch(self, project, branch_name):
        self._run_git(project, ["fetch", "origin", branch_name])
        return self._run_git(project, ["checkout", branch_name])

    def _collect_changed_modules(self, project):
        path = self._validate_addons_path(project.addons_path)
        cmd = ["git", "diff", "--name-only", "HEAD@{1}", "HEAD"]
        process = subprocess.run(cmd, cwd=path, capture_output=True, text=True, check=False, timeout=60)
        if process.returncode:
            return []
        changed_files = [line for line in process.stdout.splitlines() if line]
        modules = set()
        for changed in changed_files:
            module_name = changed.split("/", 1)[0]
            if (Path(path) / module_name / "__manifest__.py").exists():
                modules.add(module_name)
        return list(modules)

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

    def _project_path(self, project):
        path = Path(project.repo_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    def _build_env(self, token=False):
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        if token:
            env["GIT_ASKPASS"] = "echo"
            env["GIT_HTTP_PASSWORD"] = token
        return env

    def _run(self, cmd, cwd=None, env=None, timeout=300):
        process = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        output = "\n".join(filter(None, [process.stdout, process.stderr]))
        if process.returncode:
            raise UserError(_("Command failed (%s):\n%s") % (shlex.join(cmd), output))
        return output or _("Command executed successfully.")

    def _ensure_repo(self, project):
        path = Path(self._project_path(project))
        if not (path / ".git").exists():
            self._run(["git", "clone", "-b", project.branch, project.repository_url, str(path)], env=self._build_env(project.git_token_decrypted))
        return str(path)

    def _run_git(self, project, args):
        path = self._ensure_repo(project)
        cmd = ["git", *args]
        _logger.info("Running git command on %s@%s: %s", project.display_name, project.database_name, shlex.join(cmd))
        return self._run(cmd, cwd=path, env=self._build_env(project.git_token_decrypted))

    def fetch_remote_branches(self, repository_url, token=False):
        output = self._run(["git", "ls-remote", "--heads", repository_url], env=self._build_env(token), timeout=120)
        branches = []
        for line in output.splitlines():
            line = line.strip()
            if "refs/heads/" in line:
                branches.append(line.split("refs/heads/", 1)[1])
        return sorted(set(branches))

    def check_repo(self, project):
        path = self._ensure_repo(project)
        output = self._run_git(project, ["remote", "get-url", "origin"])
        if project.repository_url and project.repository_url.strip() not in output.strip():
            return False, _("Repository URL mismatch. Expected %(expected)s and got %(actual)s") % {
                "expected": project.repository_url,
                "actual": output.strip(),
            }
        return True, _("Repository is configured correctly at %(path)s") % {"path": path}

    def pull(self, project):
        self._run_git(project, ["fetch", "origin"])
        result = self._run_git(project, ["pull", "origin", project.branch])
        changed_modules = self._collect_changed_modules(project)
        if changed_modules and project.database_name == project.env.cr.dbname:
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
        path = self._project_path(project)
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

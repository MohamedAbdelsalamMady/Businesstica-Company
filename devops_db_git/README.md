# Database DevOps Git (Odoo 18)

Simple database-aware DevOps module for Odoo 18.

## What is this module?
This module lets DevOps users manage Git pull/push/checkouts for Odoo projects from inside Odoo.

## Main goal
Keep deployment operations organized per project database while keeping the form simple for non-technical users.

## Simple UX changes
- No manual `addons_path` input.
- User selects the target `database_name` from available PostgreSQL databases.
- Repository branches are fetched from remote (`git ls-remote`) and shown in **Remote Branches**.
- Computed local repository path is shown as read-only (`repo_path`) based on:
  - `devops_db_git.repositories_base_path` (default: `/mnt/extra-addons/devops_projects`)
  - selected database name

## Security
- Restricted to `DevOps Admin` group.
- Git token stored encrypted using Fernet key in `ir.config_parameter`.

## Notes
- Pull/push works on the selected project repository path.
- Auto-upgrade runs only when current Odoo session DB == selected project DB.
- Use **Fetch Branches** after entering repo URL and token.

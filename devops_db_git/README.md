# Database DevOps Git (Odoo 18)

Database-aware DevOps module that binds each Odoo database to one isolated Git project.

## Highlights
- One `devops.project` record per database (`database_name` = `env.cr.dbname`)
- Pull/push/branch operations executed only on the active database project
- Path validation to prevent invalid repositories
- Encrypted Git token storage (Fernet key in system parameters)
- Deployment logs with operation type and result
- Scheduled auto-pull per project (within current DB scope)
- Automatic upgrade of changed installed modules after pull

## Security Model
- DevOps operations are restricted to `DevOps Admin` group.
- Cross-database actions are blocked at model level.
- Token is encrypted before persisting in `encrypted_git_token`.

## Deployment Flow
1. Open **DevOps > Projects** inside a database.
2. Create project and configure:
   - Repository URL
   - Branch
   - Addons path (local git checkout)
3. Validate project
4. Use Pull/Push actions
5. Review logs in **DevOps > Deployment Logs**

## Notes
- Module assumes Linux server paths.
- Ensure repository credentials are configured or token is provided.
- Cron executes in each database separately and affects only records in that DB.

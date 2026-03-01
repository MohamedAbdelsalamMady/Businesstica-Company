# Architecture

## Layers

### 1) Models
- `devops.project`
  - Database identity binding (`database_name`)
  - Git project metadata
  - User actions (`pull`, `push`, `checkout`, `validate`)
  - Auto-upgrade orchestration
- `devops.deploy.log`
  - Immutable operation history

### 2) Service Layer
- `devops.git.service` abstract model:
  - Validates addons path
  - Runs controlled `subprocess` git commands
  - Verifies repository consistency
  - Calculates changed modules from git diff

### 3) Scheduler
- `ir.cron` calls `devops.project.cron_auto_pull`
- Runs every 10 minutes per DB and only for `auto_pull=True`

### 4) Security
- Group: `devops_db_git.group_devops_admin`
- Access:
  - `devops.project`: full for group
  - `devops.deploy.log`: read-only for group
- Runtime checks prevent any cross-database operation

## Anti Interference Rules
- Project is automatically stamped with current db on create.
- Domain and constraints rely on `env.cr.dbname`.
- Any mismatch raises `AccessError` or `ValidationError`.

## Upgrade Strategy
After successful pull:
1. service computes changed top-level modules
2. model upgrades installed modules only
3. operation gets logged with details

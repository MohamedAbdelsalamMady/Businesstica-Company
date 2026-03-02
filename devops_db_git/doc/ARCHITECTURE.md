# Architecture

## Models
- `devops.project`
  - `database_name`: selected target DB
  - `repository_url`
  - `branch`
  - `repo_path` (computed, read-only)
  - `branch_ids`: fetched remote branches
- `devops.project.branch`
  - stores fetched branch names per project
- `devops.deploy.log`
  - operation log with selected database name

## Service layer
- `devops.git.service`
  - computes repository path from project
  - auto-clones missing repository
  - pull/push/checkout operations
  - fetches remote branches via `git ls-remote --heads`

## Scheduler
- `cron_auto_pull` runs for active projects with `auto_pull=True`

## Simplicity decisions
- Removed manual `addons_path` input from UI.
- Added database selector directly in project form.
- Added one-click **Fetch Branches** button.

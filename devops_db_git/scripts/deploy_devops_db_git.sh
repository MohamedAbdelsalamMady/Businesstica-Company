#!/usr/bin/env bash
set -euo pipefail

# Deploy helper for Odoo 18 module: devops_db_git
# Usage:
#   ./deploy_devops_db_git.sh \
#     --src /path/to/repo/devops_db_git \
#     --dst /mnt/extra-addons/devops_db_git \
#     --db my_database \
#     --odoo-bin /usr/bin/odoo

SRC=""
DST=""
DB=""
ODOO_BIN=""
ODOO_SERVICE="odoo"
RESTART_SERVICE="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src) SRC="$2"; shift 2 ;;
    --dst) DST="$2"; shift 2 ;;
    --db) DB="$2"; shift 2 ;;
    --odoo-bin) ODOO_BIN="$2"; shift 2 ;;
    --service) ODOO_SERVICE="$2"; shift 2 ;;
    --no-restart) RESTART_SERVICE="0"; shift ;;
    *)
      echo "Unknown arg: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$SRC" || -z "$DST" || -z "$DB" || -z "$ODOO_BIN" ]]; then
  echo "Missing required args."
  echo "Required: --src --dst --db --odoo-bin"
  exit 1
fi

if [[ ! -d "$SRC" ]]; then
  echo "Source module not found: $SRC"
  exit 1
fi

if [[ ! -f "$SRC/__manifest__.py" ]]; then
  echo "Source path doesn't look like an Odoo module (__manifest__.py missing): $SRC"
  exit 1
fi

echo "[1/6] Pre-check view types in source..."
if rg -n "<tree>|tree,form" "$SRC/views"/*.xml; then
  echo "ERROR: source still contains deprecated tree view syntax for Odoo 18."
  exit 1
fi

echo "[2/6] Sync module to destination..."
mkdir -p "$DST"
rsync -a --delete "$SRC/" "$DST/"

echo "[3/6] Verify deployed files..."
rg -n "<list>|list,form" "$DST/views"/*.xml || true
if rg -n "<tree>|tree,form" "$DST/views"/*.xml; then
  echo "ERROR: deployed module still contains tree syntax."
  exit 1
fi

echo "[4/6] Restart Odoo service (optional)..."
if [[ "$RESTART_SERVICE" == "1" ]]; then
  sudo systemctl restart "$ODOO_SERVICE"
  sudo systemctl --no-pager --full status "$ODOO_SERVICE" | head -n 20 || true
else
  echo "Skipped service restart by request (--no-restart)."
fi

echo "[5/6] Upgrade module in target database..."
"$ODOO_BIN" -d "$DB" -u devops_db_git --stop-after-init

echo "[6/6] Done. Module deployed and upgraded for DB: $DB"

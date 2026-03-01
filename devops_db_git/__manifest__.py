{
    "name": "Database DevOps Git",
    "summary": "Database-aware Git DevOps operations per Odoo project database",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "Businesstica",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/devops_security.xml",
        "security/ir.model.access.csv",
        "views/devops_project_views.xml",
        "views/devops_deploy_log_views.xml",
        "data/devops_cron.xml"
    ],
    "application": True,
    "installable": True,
}

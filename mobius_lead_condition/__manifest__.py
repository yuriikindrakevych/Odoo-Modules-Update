{
    "name": "Mobius Lead Condition",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "18.0.0.0.5",
    "summary": "Mobius customization",
    "description": "Mobius Lead Condition",
    "depends": ["crm", "sales_team"],
    "data":
    [
        "security/ir.model.access.csv",

        "views/lead_condition_views.xml",
        "views/menu_views.xml",
        "views/crm_lead_views.xml",
        "views/crm_team_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}

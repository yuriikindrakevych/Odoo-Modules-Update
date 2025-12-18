{
    "name": "Mobius Contact Form Aklima",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "18.0.0.0.2",
    "summary": "Mobius customization",
    "description": "Mobius Contact Form Aklima",
    "depends": [
        "base",
        "sales_team",
        "mobius_login_screen_api",
        "mobius_contact_priority",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/contact_stage_menu.xml",
    ],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}

# -*- coding: utf-8 -*-
{
    "name": "Mobius Login Screen API",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "0.6",
    "category": "Sales/Contacts",
    "sequence": 1,
    "summary": "Mobius customization",
    "description": "Mobius customization",
    "depends": [
        "base",
        "contacts",
        "crm",
        "base_api",
        "openapi",
        "mobius",
        "mobius_turbosms",
        "mobius_lead_from_api",
        "mobius_auto_login"
    ],
    "data":
    [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/code_generation_views.xml",
        "data/scheduler_code_generation_cleaner.xml",
    ],
    "application": True,
    "license": "AGPL-3",
}

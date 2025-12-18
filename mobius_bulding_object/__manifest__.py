# -*- coding: utf-8 -*-
{
    "name": "Mobius Bulding Object",
    "category": "Sales/Contacts",
    "sequence": 1,
    "version": "18.0.0.12",

    "summary": "Mobius customization",
    "description": """Mobius customization""",

    "depends": [
        "base",
        "contacts",
        "sale",
        "sale_crm"
    ],

    "data":
    [
        "security/ir.model.access.csv",
        "views/building_object_views.xml",
        "views/sale_order_views.xml",
        "views/crm_lead_views.xml",
        "views/res_partner_views.xml",
        "data/sequence.xml"
    ],
    "application": True,
    "license": "AGPL-3",
}

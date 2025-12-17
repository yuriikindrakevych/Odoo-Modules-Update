# -*- coding: utf-8 -*-
{
    "name": "Mobius Create Lead From Api",
    "category": "Sales/Contacts",
    "version": "0.1.4",

    "summary": "Mobius customization",
    "description": """Mobius customization""",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",

    "depends": ["base", "contacts", "crm", "base_api", "openapi", "mobius", "mobius_product_sizes", "phone_validation"],
    "data":
    [
        "security/ir.model.access.csv",
        "data/crm_lead_sequence_data.xml",
        "views/crm_lead_views.xml",
        "views/res_users_views.xml",
        "data/crm_lead_reg_send_data.xml",
        "views/res_partner_views.xml",
    ],

    "sequence": 1,
    "application": True,
    "license": "AGPL-3",
}

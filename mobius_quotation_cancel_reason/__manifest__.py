# -*- coding: utf-8 -*-
{

    "name": "Mobius Quotation Cancel Reason",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "category": "Sales",
    "sequence": 1,
    "version": "0.4",
    "summary": "Mobius customization",
    "description": "Mobius customization",
    "depends": ["base", "sale", "crm", "mobius_portal_aklima"],
    "data":
    [
        "security/ir.model.access.csv",
        "views/sale_views.xml",
        "wizard/mobius_cancel_quotation_views.xml",
    ],
    "application": True,
    "license": "AGPL-3",
}

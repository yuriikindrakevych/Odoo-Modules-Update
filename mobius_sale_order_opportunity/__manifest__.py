# -*- coding: utf-8 -*-
{
    "name": "Mobius Sale Order Opportunity",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "1.0.1",
    "description": "Model Sale Order Opportunity",
    "installable": True,
    "application": True,
    # any module necessary for this one to work correctly
    "depends": ["base", "sale", "sale_crm"],
    "data": [
        "views/view_sale_order.xml",
    ],
    "license": "AGPL-3",
}

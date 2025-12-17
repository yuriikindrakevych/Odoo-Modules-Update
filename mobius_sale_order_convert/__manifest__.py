# -*- coding: utf-8 -*-
{
    "name": "Mobius Sale Order Convert",
    "description": "Mobius Sale Order Convert",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "1.0.0",
    "installable": True,
    "application": False,
    # any module necessary for this one to work correctly
    "depends": ["base", "sale"],
    "data": [
        "views/view_sale_order.xml",
    ],
    "license": "Other proprietary",
}

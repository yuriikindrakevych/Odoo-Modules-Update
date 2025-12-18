# -*- coding: utf-8 -*-
{
    "name": "Mobius Skip Check Balanced",
    "description": "Skip Check Balanced (in Account Move)",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "18.0.1.0.0",
    "installable": True,
    "application": False,
    # any module necessary for this one to work correctly
    "depends": ["base", "account"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "license": "AGPL-3",
}

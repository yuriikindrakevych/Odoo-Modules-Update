#!/usr/bin/python3
# -*- coding: utf-8 -*-
{
    "name": "Mobius Portal",
    "version": "18.0.0.1.6",
    "category": "Sales/Contacts",
    "sequence": 1,

    "summary": "Mobius customization",
    "description": """Mobius customization""",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    
    "depends": 
    [
        "base", 
        "portal", 
        "purchase", 
        "hr_timesheet", 
        "project", 
        "sale_management", 
        "sale", 
        "website_sale", 
        "mobius_sale_order_reports", 
        "account",
        "mobius_automatic_delivery_sale_order",
        "website_sale_delivery",
        "sale_product_configurator",
    ],
    "data": 
    [
        "data/scheduler_validity_period.xml",
        "views/portal_hide_menu_views.xml",
        "views/portal_template_building_object_views.xml",
        "views/portal_sale_order_views.xml",
        "views/portal_shop_views.xml",
        "views/res_config_settings_views.xml",
        "views/portal_pay_now_views.xml",
        "views/stock_location_views.xml",
        "views/portal_building_object_form.xml",
        "views/product_views.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'mobius_portal_aklima/static/**/*',
        ],
    },

    "sequence": 1,
    "application": True,
    "license": "AGPL-3",
}

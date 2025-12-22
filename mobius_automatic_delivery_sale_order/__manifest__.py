# -*- coding: utf-8 -*-
{
    "name": "Mobius Automatic Delivery Sale Order",
    "version": "18.0.1.0.0",

    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "summary": "Mobius customization",
    "description": "Mobius customization",
    "category": "Sales/Contacts",
    "sequence": 1,

    "depends": [
        "base",
        "sale",
        "delivery",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/automatic_delivery_sale_order_views.xml",
        "views/res_config_settings_views.xml",
        "views/delivery_carrier_views.xml",
    ],

    "installable": True,
    "application": True,
    "license": "AGPL-3",
}
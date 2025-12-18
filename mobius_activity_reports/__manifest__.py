#!/usr/bin/python3
# -*- coding: utf-8 -*-
{
    "name": "Mobius Activity Reports",
    "version": "18.0.1.0.1",

    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "summary": "Mobius customization",
    "description": "Mobius customization",
    "category": "Hidden",
    "sequence": 1,

    "depends": [
        "mail",
        "contacts",
        "crm",
        "purchase",
        "base",
        "sale"
    ],

    "data":
    [
        "data/mail_type_data.xml",
        "security/ir.model.access.csv",
        "views/res_partner_report_views.xml",
        "views/sale_order_report_views.xml",
        "views/purchase_order_report_views.xml",
        "views/general_report_views.xml",
    ],

    "installable": True,
    "application": True,
    "license": "AGPL-3",
}

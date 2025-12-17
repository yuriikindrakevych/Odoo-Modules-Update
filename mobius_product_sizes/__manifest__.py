#!/usr/bin/python3
# -*- coding: utf-8 -*-
{
    "name": "mobius_product_sizes",
    "category": "Product",
    "summary": "Mobius customization for Odoo 15",
    "description": """We add the Length, Width, and Height for automatic volume calculation""",
    "installable": True,
    "author" : "Mobius team",
    "license": "Other proprietary",
    "version": "1.0.0",
    "depends": [
        "product",
        "uom",
        "sale",
        "crm",
        "contacts",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/res_partner_views.xml",
        "views/crm_lead_views.xml",
    ],
}

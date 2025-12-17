# -*- coding: utf-8 -*-
{
    "name": "Mobius",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "category": "Sales/Contacts",
    "sequence": 1,
    "version": "0.3",
    "summary": "Mobius customization",
    "description": "Mobius customization",
    
    "depends": ["base", "contacts", "crm", "sale", "project", "barcodes_generator_abstract", "mobius_catalogue_koatuu"],
    "data":
    [
        "data/barcode_rule.xml",
        "data/scheduler_currency.xml",
        "data/currency_rate_source.xml",

        "views/res_partner_views.xml",
        "views/res_bank_views.xml",
        "views/view_product_template.xml",
        "views/view_product_product.xml",
        "views/project_task_views.xml",
        "views/project_milestone_views.xml",
        "views/product_packaging.xml",
        "views/res_config_settings_views.xml",
        "views/res_currency_views.xml",
        "views/sale_order_views.xml",
        "security/ir.model.access.csv",
        "views/product_category_views.xml",
    ],
    "application": True,
    "license": "AGPL-3",
}

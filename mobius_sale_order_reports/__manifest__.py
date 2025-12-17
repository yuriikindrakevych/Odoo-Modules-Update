# -*- coding: utf-8 -*-
{
    "name": "Mobius Sale Order Reports",
    "version": "15.0.0.3.3",
    "category": "Sales/Contacts",
    
    "summary": "Mobius customization",
    "description": """Mobius customization""",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",

    "depends": ["base", "contacts", "sale_management", "web", "sale", "mobius_bulding_object", "mobius", "mobius_contact_by_vat"],
    "data":
    [
        "security/ir.model.access.csv",
        "views/sale_report_views.xml",
        "views/account_move_views.xml",
        "views/profile_res_partner_bank_views.xml",
        "views/res_currency_views.xml",
        "views/sale_order_line_views.xml",
        "views/res_partner_views.xml",
        "views/product_pricelist_views.xml",
        "data/report_sale_order_zamowienie.xml",
        "data/report_sale_order_zamowienie_en.xml",
        "data/report_account_move_vat_correction_invoice.xml",
        "data/report_account_move_vat_correction_invoice_en.xml",
        "data/report_sale_order_pro_forma.xml",
        "data/report_sale_order_pro_forma_en.xml",
        "data/report_sale_order_zamowienie_short.xml",
        "data/report_sale_order_zamowienie_short_en.xml",

    ],

    "sequence": 1,
    "application": True,
    "license": "AGPL-3",
}

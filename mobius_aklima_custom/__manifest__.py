{
    "name": "Mobius Aklima Customization",
    "category": "Customization",
    "version": "0.2.7",

    "summary": "Mobius customization",
    "description": "Aklima Customization",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",

    "depends": [
        "base",
        "mail",
        "mobius_quotation_cancel_reason",
        "product",
        "sale",
        "sale_crm",
        "sale_stock",
        "stock",
    ],

    "data": [
        "security/ir.model.access.csv",
        "security/product_security_views.xml",
        "views/sale_order.xml",
        "views/stock_location_views.xml",
        "views/sale_order_status.xml",
        "views/crm_lead_views.xml",
    ],

    "installable": True,
    "application": True,
    "license": "AGPL-3",
}

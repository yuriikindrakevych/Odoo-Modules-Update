{
    "name": "Mobius lead contact import",
    "category": "Sales/Contacts",
    "version": "18.0.0.1.5",

    "summary": "Mobius customization",
    "description": "Advanced contacts importing from file as leads",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",

    "depends": [
        "base",
        "contacts",
    ],

    "data": [
        "data/lead_res_partner_category_tag.xml",
        "views/res_partner_inherited_views.xml",
    ],

    "assets":
    {
       "web.assets_backend":
       [
            "mobius_lead_contact_import/static/src/js/lead_import_menu.js",
            "mobius_lead_contact_import/static/src/xml/**/*",
       ],
    },

    "installable": True,
    "license": "AGPL-3",
}

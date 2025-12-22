{
    "name": "Mobius Lead by the VAT",
    "category": "Sales/Contacts",
    "version": "18.0.0.1.2",
    
    "summary": "Mobius customization",
    "description": "Creating of Lead by the VAT code",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",

    "depends": [
        "base", 
        "contacts", 
        "mobius", 
        "crm",
        "mobius_catalogue_koatuu",
    ],

    "assets":
    {
       "web.assets_backend":
       [
            "mobius_lead_by_vat/static/src/js/**/*",
            "mobius_lead_by_vat/static/src/xml/**/*",
       ],
    },

    "data": [
        "security/ir.model.access.csv",
        "views/mobius_lead_by_vat.xml",
        "views/crm_lead_inherited_tree.xml",
    ],

    "sequence": 1,
    "installable": True,
    "license": "AGPL-3",
}

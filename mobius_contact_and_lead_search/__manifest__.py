{
    "name": "Mobius Contact and Lead Search",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "18.0.0.0.2",
    "summary": "Mobius customization",
    "description": "Mobius Contact and Lead Search",
    "depends": [
        "contacts",
        "crm",
    ],

    "data":
    [
        "security/ir.model.access.csv",

        "views/general_search_by_models_views.xml",
        "views/menu_views.xml",
    ],
    "application": True,
    "installable": True,
    "license": "AGPL-3",
}

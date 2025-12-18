{
    "name": "Mobius Catalogue KOATUU",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "18.0.0.0.3",
    "summary": "Mobius customization",
    "description": "Mobius Catalogue KOATUU",
    "depends": ["base", "contacts"],
    "data":
    [
        "data/res.country.state.xml",
        "data/mobius_catalogue_koatuu.settlement_type.xml",
        "data/mobius_catalogue_koatuu.settlement.xml",

        "views/settlement_type_views.xml",
        "views/settlement_views.xml",
        "views/customize_menu.xml",
        "views/res_partner_views.xml",
        "views/res_bank_views.xml",

        "security/ir.model.access.csv",
    ],
    "application": True,
    "installable": True,

    "license": "Other proprietary",
}

{
    "name": "Mobius Contact by the VAT",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "description": "Creating of Contact by the VAT code",
    "version": "18.0.1.0.0",
    
    "depends": ["base", "contacts", "mobius_catalogue_koatuu", ],
    # Assets disabled - need OWL rewrite for Odoo 18
    # "assets":
    # {
    #    "web.assets_backend":
    #    [
    #        "mobius_contact_by_vat/static/src/js/open_wizard_contact_by_vat_tree.js",
    #        "mobius_contact_by_vat/static/src/js/open_wizard_contact_by_vat_kanban.js",
    #        "mobius_contact_by_vat/static/src/xml/open_wizard_contact_by_vat_tree.xml",
    #        "mobius_contact_by_vat/static/src/xml/open_wizard_contact_by_vat_kanban.xml",
    #    ],
    # },
    "data": [
        "security/ir.model.access.csv",
        "views/mobius_contact_by_vat.xml",
        "views/res_partner_inherited_tree.xml",
	    "views/res_partner_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}

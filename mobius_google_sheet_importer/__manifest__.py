{
    "name": "Mobius Aklima Google Sheet Importer",
    "summary": "Aklima Customization",
    "version": "18.0.1.0.0",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "category": "Customization",
    "depends": [
        "crm",
        "google_sheet_importer",
        "mobius_lead_contact_import",
    ],
    "data": [
        "views/google_sheet_importer_views.xml"
    ],
    "external_dependencies": {
        "python": ["gspread"],
    },
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}

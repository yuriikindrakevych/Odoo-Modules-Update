{
    "name": "Google Sheet Importer",
    "summary": "Dynamic models and field mapping with the ability to import multiple Google Sheets into any Odoo model and fields using scheduled actions (cron)",
    "version": "15.0.1.0.0",
    "author": "Jothimani Rajagopal",
    "website": "https://www.linkedin.com/in/jothimani-r/",
    "category": "Tools",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/google_sheet_importer_views.xml"
    ],
    "images": ["static/description/banner.png"],
    "external_dependencies": {
        "python": ["gspread"],
    },
    "price": 69.99,
    "currency": 'USD',
    "installable": True,
    "application": False,
    "license": "OPL-1",
}

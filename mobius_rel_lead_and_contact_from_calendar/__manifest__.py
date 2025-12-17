{
    "name": "Mobius Related Lead and Contact From Calendar Event",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "version": "15.0.0.0.5",
    "summary": "Mobius customization",
    "description": "Mobius Related Lead and Contact From Calendar Event",
    "depends": ["crm"],
    "data":
    [
        "security/ir.model.access.csv",
        "wizard/choosing_lead_and_contact.xml",

        "views/calendar_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}

# -*- coding: utf-8 -*-
{

    "name": "Mobius Advanced Calendar",
    "author": "Mobius ERP",
    "website": "https://erp-mobius.com",
    "category": "Sales/Contacts",
    "sequence": 1,
    "version": "0.1",
    "summary": "Mobius customization",
    "description": "Mobius customization",
    "depends": ["base", "calendar", "mail", "crm", "web", "sale"],
    "data":
    [
        "report/report.xml",
        "views/calendar_advanced_views.xml",
    ],
    "assets": {
        "web.assets_qweb": [
            "mobius_advanced_calendar_aklima/static/src/xml/base_calendar.xml",
        ],
    },
    "application": True,
    "license": "AGPL-3",
}

# -*- coding: utf-8 -*-
{
    "name": "Mobius Lead Today Task",
    "category": "Sales/Contacts",
    "sequence": 1,
    "version": "0.1",
    "summary": "Mobius customization",
    "description": "Mobius customization",

    "depends": ["base", "crm", "purchase", "sale", "contacts", "mobius_advanced_calendar_aklima"],
    "data":
    [
        "security/ir.model.access.csv",
        "views/menu_lead_today_task_views.xml",
    ],
    
    "application": True,
    "license": "Other proprietary",
}

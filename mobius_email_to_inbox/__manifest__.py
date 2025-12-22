# -*- coding: utf-8 -*-
{
    "name":        "mobius_email_to_inbox",
    "author":      "Mobius ERP",
    "website":     "https://erp-mobius.com",
    "category":    "Tools",
    "summary":     "Puts incomming emails to user's inbox",
    "description": """
        This module processes all the incoming emails that weren't processed by the aliases.
        It compares the address with the user's login, email, work_email, and provate_email and puts the message into the user's inbox.
        If no user is found, the email will be put into the Administrator's inbox.
    """,
    "category":    "Discuss",
    "version":     "18.0.1.0.1",
    "depends":     ["mail"],
    "application": False,
    "license":     "AGPL-3",
}
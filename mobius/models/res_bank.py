#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _


class ResBank(models.Model):
    _inherit = "res.bank"

    full_name = fields.Char("Full name")
    iban_code = fields.Char("IBAN")
    account_number = fields.Char("Account number")
    edrpou_number = fields.Char("EDRPOU number")
    itn_number = fields.Char("Individual Taxpayer Number")  #ІПН
    swift_code = fields.Char("SWIFT")

#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _

class ResPartner(models.Model):
    _inherit = "res.partner"

    certificate_data = fields.Char(string="Certificate data")
    trade_guardian_code = fields.Char(string="Trade code")

    def check_exist_record_mobile(self, phone):
        search_record = self.search_count([("phone", "=", phone)])
        if search_record > 0:
            return True
        return False

    def check_exist_record_email(self, email):
        search_record = self.search_count([("email", "=", email)])
        if search_record > 0:
            return True
        return False
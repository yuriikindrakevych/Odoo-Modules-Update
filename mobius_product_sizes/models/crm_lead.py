#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Lead(models.Model):
    _inherit = "crm.lead"

    certificate_data = fields.Char(string="Certificate data")
    trade_guardian_code = fields.Char(string="Trade code")
    vat = fields.Char(string="Identification Number")
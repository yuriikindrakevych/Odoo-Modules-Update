#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _

class ResUsers(models.Model):
    _inherit = "res.users"

    trade_guardian_code = fields.Char(string="Trade code")
    access_code_to_external_systems = fields.Char("Access code to external systems")
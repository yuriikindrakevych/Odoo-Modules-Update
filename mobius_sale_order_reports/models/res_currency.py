#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResCurrency(models.Model):
    _inherit = "res.currency"

    default_bank_id = fields.Many2one("res.partner.bank",
        string="Bank Account")
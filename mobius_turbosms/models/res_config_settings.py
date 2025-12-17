#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    token_for_turbosms = fields.Char(string="Token for TurboSMS", config_parameter="token_for_turbosms")
    turbosms_enable = fields.Boolean(string="Enable TurboSMS", config_parameter="turbosms_enable")
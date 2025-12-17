#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    aclima_API_URL = fields.Char(string="Aclima API URL", config_parameter="aclima_API_URL",
                                 default="http://rusmtp.aclima.com.ua:65080/AKLIMA/hs/inventory/bilance")
    aclima_API_login = fields.Char(string="Aclima API Login", config_parameter="aclima_API_login", default="WEB_USER2")
    aclima_API_password = fields.Char(string="Aclima API password", config_parameter="aclima_API_password")

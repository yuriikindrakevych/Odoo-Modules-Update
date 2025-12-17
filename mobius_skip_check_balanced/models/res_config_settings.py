#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_move_check_balanced_skip = fields.Boolean(
        string="Skip check balanced",
        config_parameter="account_move_check_balanced_skip"
    )

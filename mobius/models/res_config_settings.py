#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    currencies_get_exchange_rate = fields.Boolean(string="Automatic refresh of currency rates", config_parameter="currencies_get_exchange_rate")
    currency_rate_source = fields.Many2one("mobius.currency.rate.source", string="Source", config_parameter="currency_rate_source")

    @api.onchange("currencies_get_exchange_rate")
    def _onchange_currencies_get_exchange_rate(self):
        if self.currencies_get_exchange_rate:
            if not self.currency_rate_source:
                source = self.env["mobius.currency.rate.source"].search_read([("name", "=", "PrivatBank")], fields=["name"])
                self.currency_rate_source = source[0]["id"]

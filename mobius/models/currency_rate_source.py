#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api

import requests
import json

class CurrencyRateSource(models.Model):
    _name = "mobius.currency.rate.source"
    _description = "Currency Rate Source"

    name = fields.Text("Name", required=True)

    _sql_constraints = [
        ("currency_rate_source_name_uniq", "unique(name)", "Name must be unique!"),
    ]

    @api.model
    def load_privat_bank_rates(self):
        URL_PRIVAT = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
        data = requests.get(URL_PRIVAT)
        return json.loads(data.text)

    @api.model
    def load_mono_bank_rates(self):
        URL_MONO = "https://api.monobank.ua/bank/currency"
        data = requests.get(URL_MONO, timeout=10)
        mono_dict = json.loads(data.text)
        data.close()
        for item in mono_dict:
            if item["currencyCodeB"] == 980:
                item["currencyCodeB"] = "UAH"

            if item["currencyCodeA"] == 840:
                item["currencyCodeA"] = "USD"

            if item["currencyCodeA"] == 978:
                item["currencyCodeA"] = "EUR"
        return mono_dict

    @api.model
    def load_nbl_rate_certain_currency(self, name_currency):
        if name_currency:
            URL_NBL = "https://api.nbp.pl/api/exchangerates/rates/a/"+ name_currency + "/?format=json"
            data = requests.get(URL_NBL)
            if data.status_code == 200:
                return json.loads(data.text)
        return False



#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

import datetime
import logging

_logger = logging.getLogger(__name__)


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    inv_rate = fields.Float(digits=0, group_operator="avg", help="The rate (sell) of the currency to the currency of rate 1", string="Technical Rate (sell)")
    inverse_company_rate = fields.Float(digits=0, compute="_compute_inverse_company_rate", inverse="_inverse_inverse_company_rate", group_operator="avg")

    @api.model
    def sync_action(self):
        if self.is_enabled():
            self.synchronize()

    @api.model
    def is_enabled(self):
        currencies_get_exchange_rate = self.env["ir.config_parameter"].sudo().get_param("currencies_get_exchange_rate")
        return currencies_get_exchange_rate

    @api.depends("res.currency.rate")
    @api.model
    def create_rate_record(self, company_id, currency_id, buy_rate, sell_rate):
        try:
            today = datetime.datetime.utcnow().replace(tzinfo=None)
            items = self.env["res.currency.rate"].search([("name", "=", today), ("currency_id", "=", currency_id), ("company_id", "=", company_id)])
            if items:
                items.unlink()

            self.env["res.currency.rate"].create({
                "rate":        buy_rate,
                "inv_rate":    sell_rate,
                "currency_id": currency_id,
                "company_id":  company_id,
            })
            self.env.cr.commit()
        except Exception:
            logging.exception("Error creating currency rate: company_id=%s, currency_id=%s, buy_rate=%s, sell_rate=%s",
                str(company_id), str(currency_id), str(buy_rate), str(sell_rate))

    @api.model
    def synchronize(self):
        currencies_get_exchange_rate = int(self.env["ir.config_parameter"].sudo().get_param("currency_rate_source"))
        if currencies_get_exchange_rate == self.env.ref("mobius.currency_rate_source_privatbank").id:
            self.synchronize_UAH_privat()
        if currencies_get_exchange_rate == self.env.ref("mobius.currency_rate_source_monobank").id:
            self.synchronize_UAH_mono()
        if currencies_get_exchange_rate == self.env.ref("mobius.currency_rate_source_nbl").id:
            self.synchronize_PLN_nbl()

    @api.model
    def synchronize_UAH_privat(self):
        companies  = self.list_companies_having_UAH()
        currencies = self.list_active_currencies()
        rates      = self.load_privat_rates()
        for company in companies:
            for currency in currencies:
                for rate in rates:
                    if (rate["ccy"] == currency["name"]) and (rate["base_ccy"] == "UAH"):
                        self.create_rate_record(company["id"], currency["id"], rate["buy"], rate["sale"])

    @api.model
    def synchronize_UAH_mono(self):
        companies  = self.list_companies_having_UAH()
        currencies = self.list_active_currencies()
        rates      = self.load_mono_rates()
        for company in companies:
            for currency in currencies:
                for rate in rates:
                    if (rate["currencyCodeA"] == currency["name"]) and (rate["currencyCodeB"] == "UAH"):
                        self.create_rate_record(company["id"], currency["id"], rate["rateSell"], rate["rateBuy"])

    @api.model
    def synchronize_PLN_nbl(self):
        companies  = self.list_companies_having_certain_currency("PLN")
        currencies = self.list_active_currencies_without_main_currency("PLN")
        for company in companies:
            for currency in currencies:
                rate = self.load_nbl_rate_certain_currency(currency["name"])
                if rate:
                    if rate["code"] == currency["name"]:
                        self.create_rate_record(company["id"], currency["id"], rate["rates"][0]["mid"], rate["rates"][0]["mid"])

    @api.model
    def list_companies_having_UAH(self):
        return self.env["res.company"].search_read([("currency_id", "=", "UAH")], fields=["id", "name"])

    @api.model
    def list_active_currencies(self):
        return self.env["res.currency"].search_read([("active", "=", True,), ("name", "!=", "UAH")], fields=["id", "name"])

    @api.model
    def list_companies_having_certain_currency(self, certain_currency):
        return self.env["res.company"].search_read([("currency_id", "=", certain_currency)], fields=["id", "name"])

    @api.model
    def list_active_currencies_without_main_currency(self, main_currency):
        return self.env["res.currency"].search_read([("active", "=", True,), ("name", "!=", main_currency)], fields=["id", "name"])

    @api.model
    def load_privat_rates(self):
        return self.env["mobius.currency.rate.source"].load_privat_bank_rates()

    @api.model
    def load_mono_rates(self):
        return self.env["mobius.currency.rate.source"].load_mono_bank_rates()

    @api.model
    def load_nbl_rate_certain_currency(self, certain_currency):
        return self.env["mobius.currency.rate.source"].load_nbl_rate_certain_currency(certain_currency)


    def _get_last_inv_rates_for_companies(self, companies):
        return {
            company: company.currency_id.rate_ids.sudo().filtered(lambda x: (
                x.rate
                and x.company_id == company or not x.company_id
            )).sorted("name")[-1:].inv_rate or 1
            for company in companies
        }

    def _get_latest_inv_rate(self):
        return self.currency_id.rate_ids.sudo().filtered(lambda x: (
            x.inv_rate
            and x.company_id == (self.company_id or self.env.company)
            and x.name < (self.name or fields.Date.today())
        )).sorted("name")[-1:]

    @api.depends("inv_rate", "name", "currency_id", "company_id", "currency_id.rate_ids.inv_rate")
    def _compute_inverse_company_rate(self):
        last_rate = self.env["res.currency.rate"]._get_last_inv_rates_for_companies(self.company_id | self.env.company)
        for currency_rate in self:
            company = currency_rate.company_id or self.env.company
            currency_rate.inverse_company_rate = 1.0 / (currency_rate.inv_rate or self._get_latest_inv_rate().inv_rate or 1.0) / last_rate[company]

    @api.onchange("inverse_company_rate")
    def _inverse_inverse_company_rate(self):
        last_rate = self.env["res.currency.rate"]._get_last_inv_rates_for_companies(self.company_id | self.env.company)
        for currency_rate in self:
            company = currency_rate.company_id or self.env.company
            currency_rate.inv_rate = 1.0 / currency_rate.inverse_company_rate * last_rate[company]


class Currency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        currency_rates = (from_currency + to_currency)._get_rates(company, date)
        res = currency_rates.get(from_currency.id) / currency_rates.get(to_currency.id)
        return res

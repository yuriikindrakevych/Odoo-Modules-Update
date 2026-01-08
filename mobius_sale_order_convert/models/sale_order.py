#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    company_currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    amount_untaxed_convert = fields.Monetary(string="Untaxed Amount (Converted)", store=True, readonly=True,
                                             currency_field="company_currency_id",
                                             compute="_amount_untaxed_convert")

    @api.depends("amount_untaxed")
    def _amount_untaxed_convert(self):
        for order in self:
            company_currency = self.env.company.currency_id
            if order.currency_id.id != company_currency.id:
                # Odoo 18: compute() replaced with _convert()
                amount_convert = order.currency_id._convert(
                    order.amount_untaxed,
                    company_currency,
                    order.company_id or self.env.company,
                    fields.Date.today()
                )
                order.amount_untaxed_convert = amount_convert
            else:
                order.amount_untaxed_convert = order.amount_untaxed

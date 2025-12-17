#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_of_debt_m = fields.Float("Amount Of Debt", compute="_compute_amount_of_debt_m")
    procentage_of_payment = fields.Integer("% of payment", compute="_compute_procentage_of_payment")

    def _compute_amount_of_debt_m(self):
        for sale in self:
            total_debt = sale.amount_total
            total_debt_invoice = sum(sale.invoice_ids.mapped("amount_total_in_currency_signed"))
            total_signed = sum(sale.invoice_ids.mapped("amount_residual_signed"))
            sale.amount_of_debt_m = (total_debt - total_debt_invoice) + total_signed

    def _compute_procentage_of_payment(self):
        for sale in self:
            if sale.amount_total <= 0:
                sale.procentage_of_payment = 0
                continue
            paid = sale.amount_total - sale.amount_of_debt_m
            sale.procentage_of_payment = round((paid / sale.amount_total) * 100)
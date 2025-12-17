#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.translate import html_translate


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_validity_period_for_order_created_with_website = fields.Boolean(
        string="Validity Period For Order",
        config_parameter="use_validity_period_for_order_created_with_website")

    validity_period_for_order_created_with_website_days = fields.Integer(
        string="Validity Period For Order (Days)",
        readonly=False,
        config_parameter="validity_period_for_order_created_with_website_days")

    use_product_show_availability = fields.Boolean(
        string="Show availability Qty",
        config_parameter="use_product_show_availability")

    available_threshold = fields.Float(string="Show Threshold", default=5.0)

    out_of_stock_message = fields.Char(
        string="Out-of-Stock Message",
        translate=html_translate,
        config_parameter="out_of_stock_message")
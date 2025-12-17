#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_automatic_delivery_sale_order = fields.Boolean(
        string="Automatic Delivery Sale Order",
        config_parameter="use_automatic_delivery_sale_order")

    automatic_delivery_sale_order_source = fields.Many2one(
        "automatic.delivery.sale.order",
        string="Use",
        config_parameter="automatic_delivery_sale_order_source")

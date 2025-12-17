#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def is_enable_use_automatic_delivery_sale_order(self):
        use_automatic_delivery_sale_order = self.env["ir.config_parameter"].sudo().get_param("use_automatic_delivery_sale_order")
        return use_automatic_delivery_sale_order

    @api.model
    def get_template_automatic_delivery_sale_order(self):
        automatic_delivery_sale_order_source = self.env["ir.config_parameter"].sudo().get_param("automatic_delivery_sale_order_source")
        return self.env["automatic.delivery.sale.order"].browse(int(automatic_delivery_sale_order_source)).exists()

    def calculate_weight_in_order(self):
        weight = 0.0
        for line in self.order_line:
            weight += (line.product_id.weight * line.product_uom_qty)
        return weight

    def _create_delivery_line(self, carrier, price_unit):
        _logger.info("_create_delivery_line")
        res = super()._create_delivery_line(carrier, price_unit)

        # Змінюємо ціну тільки для певного типу доставки, інші не чіпаємо
        if not carrier.base_delivery:
            _logger.info("if not carrier.base_delivery")
            return res

        template = self.get_template_automatic_delivery_sale_order()
        if not self.is_enable_use_automatic_delivery_sale_order() or not template:
            _logger.info("if not self.is_enable_use_automatic_delivery_sale_order() or not template:")
            return res

        # Щось з цього не працює
        total = (res.order_id.amount_untaxed - res.price_unit)
        # total = (res.order_id.amount_total - res.price_unit)

        _logger.info("total=%s", total)
        if not template.the_price_is_suitable(total):
            _logger.info("if not template.the_price_is_suitable(total):")
            return res

        weight = res.order_id.calculate_weight_in_order()
        condition_is_met = template.the_weight_is_suitable(weight)

        _logger.info("weight=%s", weight)
        _logger.info("condition_is_met=%s", condition_is_met)
        _logger.info("Before res.price_unit=%s", res.price_unit)
        if condition_is_met:
            res.price_unit = template.automatic_delivery_condition_is_met
            _logger.info("if condition_is_met:")
        else:
            _logger.info("else")
            res.price_unit = template.automatic_delivery_condition_is_not_met
        _logger.info("After res.price_unit=%s", res.price_unit)
        _logger.info("return RES")
        return res


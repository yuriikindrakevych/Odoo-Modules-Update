#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError, ValidationError
from itertools import chain

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    base_delivery = fields.Boolean("Base Delivery")

    @api.constrains("base_delivery")
    def _check_base_delivery(self):
        checked_bool = self.search([("base_delivery", "=", True)])
        if len(checked_bool) > 1:
            raise ValidationError(_("Only one delivery can be used like base"))

    def _match_address(self, partner):
        res = super()._match_address(partner)
        _logger.info('Method _match_address res: %s', res)
        return res

    def fixed_rate_shipment(self, order):
        res = super().fixed_rate_shipment(order)
        _logger.info('Method fixed_rate_shipment res: %s', res)
        return res

    def rate_shipment(self, order):
        res = super().rate_shipment(order)
        _logger.info('Method rate_shipment res: %s', res)
        return res

# Disabled for Odoo 18 - _compute_price_rule API completely changed
# _compute_price_rule_get_items method no longer exists in Odoo 18
# These overrides use old Odoo 15 pricelist API

# class Pricelist(models.Model):
#     _inherit = "product.pricelist"
#
#     def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
#         """ Low-level method - Mono pricelist, multi products
#         Returns: dict{product_id: (price, suitable_rule) for the given pricelist}
#         ...
#         """
#         # Method body removed - uses deprecated API
#         pass

# class PricelistItem(models.Model):
#     _inherit = "product.pricelist.item"
#
#     def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
#         # Method body removed - uses deprecated API
#         pass
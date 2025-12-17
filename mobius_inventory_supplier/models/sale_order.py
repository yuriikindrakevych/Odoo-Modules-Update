# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    inventory_quantity = fields.Integer(compute="_sync_with_inventory", string=_("Quantity at the partner"))
    inventory_income = fields.Text(compute="_sync_with_inventory")

    @api.depends("product_id")
    def _sync_with_inventory(self):
        try:
            for line in self:
                # mandatory initialization
                line.inventory_quantity = 0
                line.inventory_income = ""

                inv_sup = self.env["inventory.supplier"].search([("product_tmpl_id", "=", line.product_id.product_tmpl_id.id)])
                for item in inv_sup:
                    if item.inventory_quantity:
                        line.inventory_quantity += item.inventory_quantity
                    if item.purchaseorders_income:
                        line.inventory_income += item.purchaseorders_income

        except Exception as ex:
            _logger.error("Exception (SaleOrderLine -> _sync_with_inventory): ", ex)

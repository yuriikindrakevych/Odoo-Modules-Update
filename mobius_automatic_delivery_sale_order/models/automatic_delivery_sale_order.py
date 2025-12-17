from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class AutomaticDeliverySaleOrder(models.Model):
    _name = "automatic.delivery.sale.order"

    name = fields.Char("Name", required=True)
    description = fields.Char("Description")
    cost = fields.Integer("Cost")
    cost_operator = fields.Selection(
        [
            ("greater_than", ">"),
            ("less_than", "<"),
            ("greater_than_or_equal_to", ">="),
            ("less_than_or_equal_to", "<="),
        ], default="greater_than",
    )
    weight = fields.Integer("Weight")
    weight_operator = fields.Selection(
        [
            ("greater_than", ">"),
            ("less_than", "<"),
        ], default="greater_than",
    )
    automatic_delivery_condition_is_met = fields.Integer()
    automatic_delivery_condition_is_not_met = fields.Integer()

    weight_operator_not_met = fields.Selection(
        [
            ("greater_than_or_equal_to", ">="),
            ("less_than_or_equal_to", "<="),
        ],
        readonly=True,
        default="less_than_or_equal_to",
    )
    weight_not_met = fields.Integer("Weight", readonly=True)

    @api.onchange("weight_operator")
    def _onchange_weight_operator(self):
        if not self.weight_operator:
            return
        if self.weight_operator == "greater_than":
            self.weight_operator_not_met = "less_than_or_equal_to"
        else:
            self.weight_operator_not_met = "greater_than_or_equal_to"

    @api.onchange("weight")
    def _onchange_weight(self):
        self.weight_not_met = self.weight

    def the_price_is_suitable(self, cost_in_order):
        if self.cost_operator == "greater_than":
            if cost_in_order > self.cost:
                return True
        elif self.cost_operator == "less_than":
            if cost_in_order < self.cost:
                return True
        elif self.cost_operator == "greater_than_or_equal_to":
            if cost_in_order >= self.cost:
                return True
        elif self.cost_operator == "less_than_or_equal_to":
            if cost_in_order <= self.cost:
                return True
        return False

    def the_weight_is_suitable(self, weight_in_order):
        if self.weight_operator == "greater_than":
            if weight_in_order > self.weight:
                return True
        elif self.weight_operator == "less_than":
            if weight_in_order < self.weight:
                return True
        return False
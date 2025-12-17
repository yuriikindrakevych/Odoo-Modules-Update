# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    opportunity_count = fields.Integer(compute="_compute_opportunity_count", readonly=True)

    @api.depends("opportunity_id")
    def _compute_opportunity_count(self):
        for item in self:
            item.opportunity_count = 1 if item.opportunity_id else 0

    def action_show_opportunity(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_opportunities")
        action["domain"] = [("id", "in", self.opportunity_id.ids)]
        action["context"] = {
            "active_test": False,
            "create": False
        }
        return action

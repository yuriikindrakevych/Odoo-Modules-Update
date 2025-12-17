#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cancel_reason_id = fields.Many2one(comodel_name="crm.lost.reason", string="Cancel Reason", readonly=True)
    cancellation_comment = fields.Char(string="Cancellation Comment", readonly=True)

    def action_cancel(self):
        # Open the cancellation wizard
        if self.state == "draft":
            return {
                "type": "ir.actions.act_window",
                "name": _("Specify the reason for cancellation"),
                "res_model": "cancel.quotation",
                "view_mode": "form",
                "target": "new",
                "context": {"active_id": self.id}
            }
        return super(SaleOrder, self).action_cancel()

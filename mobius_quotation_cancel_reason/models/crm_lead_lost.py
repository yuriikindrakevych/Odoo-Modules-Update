#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, _


class CrmLeadLost(models.TransientModel):
    _inherit = "crm.lead.lost"

    def action_lost_reason_apply(self):
        result = super().action_lost_reason_apply()
        for lead in self.env["crm.lead"].browse(self.env.context.get("active_ids")):
            # print("action_lost_reason_apply -> lead=", lead, "lead.order_ids=", lead.order_ids)
            for order in lead.order_ids:
                if order.state == "draft":
                    order.write({"cancel_reason_id": lead.lost_reason.id})
                    order._action_cancel()
        return result

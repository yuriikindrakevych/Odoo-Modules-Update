#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, _


class Lead(models.Model):
    _inherit = "crm.lead"

    # def toggle_active(self):
    #     result = super().toggle_active()
    #     for order in self.order_ids:
    #         if order.state == "cancel":
    #             order.write({"cancel_reason_id": None})
    #             order.action_draft()
    #     return result

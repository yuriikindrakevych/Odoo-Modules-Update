# -*- coding: utf-8 -*-
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        vals = super()._prepare_invoice_values(order=order, name=name, amount=amount, so_line=so_line)
        delivered = self.env.context.get("delivered")
        if delivered == True:
            vals["advance_payment_method_delivered"] = True
        else:
            vals["advance_payment_method_delivered"] = False
        return vals

    def create_invoices(self):
        self.env.context = dict(self.env.context)
        if self.advance_payment_method == "delivered":
            self.env.context.update({
                "delivered": "True",
            })
        else:
            self.env.context.update({
                "delivered": "False",
            })
        return super().create_invoices()
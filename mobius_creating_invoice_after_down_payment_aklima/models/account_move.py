from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_switch_invoice_into_refund_credit_note(self):
        for move in self:
            if move.amount_total >= -0.01:
                move.write({
                    "amount_untaxed": 0.0,
                    "amount_tax": 0.0,
                    "amount_total": 0.0
                })
            else:
                super(AccountMove, move).action_switch_invoice_into_refund_credit_note()

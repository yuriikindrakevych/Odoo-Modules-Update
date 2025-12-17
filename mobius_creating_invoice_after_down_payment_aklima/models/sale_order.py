from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        for move in moves:
            if move.amount_total <= 0.01 and move.amount_total > 0.0:
                move.write({
                    "amount_untaxed": 0.0,
                    "amount_tax": 0.0,
                    "amount_total": 0.0
                })

        return moves

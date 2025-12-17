import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_so_line(self, order, analytic_tag_ids, tax_ids, amount):
        res = super()._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)

        # Set tax_id from the first sale order line if available
        filtered_sale_order_line = order.order_line.filtered(lambda so_line: not so_line.display_type)
        if order.order_line and filtered_sale_order_line[0].tax_id.ids:
            res['tax_id'] = [(6, 0, filtered_sale_order_line[0].tax_id.ids)]
        else:
            res['tax_id'] = [(6, 0, [])]
        return res

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super()._prepare_invoice_values(order, name, amount, so_line)
        tax_amount = so_line.tax_id[0].amount if so_line.tax_id and so_line.tax_id[0].amount else 0
        res["invoice_line_ids"] = [(0, 0, {
                'name': name,
                'price_unit': amount / (1 + tax_amount / 100),
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id if not so_line.display_type and order.analytic_account_id.id else False,
            })]
        return res

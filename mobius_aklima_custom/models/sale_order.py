from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    status_ids = fields.Many2many(
        comodel_name="sale.order.status",
        string="Status", 
        tracking=True,
    )
    account_status = fields.Selection(selection=[("paid", "Paid"), ("not_paid", "Not paid"), ("partial", "Partial")],
                                      readonly=True, compute="_compute_account_status", required=False)
    shipping_status = fields.Selection(selection=[("shipped", "Shipped"), ("not_shipped", "Not shipped"), ("partial", "Partial")],
                                      readonly=True, compute="_compute_shipping_status", required=False)
    debt_amount = fields.Monetary(compute="_compute_debt_amount", readonly=True)
    so_partner_payment_ids = fields.One2many(
        comodel_name="sale.order.partner.payment",
        inverse_name="sale_order_id",
    )
    total_payments_sum = fields.Monetary(compute="_compute_total_payments_sum", currency_field="currency_id")

    @api.depends("invoice_ids", "invoice_ids.payment_state")
    def _compute_account_status(self):
        for record in self:
            paid = False
            partial = False
            not_paid = False

            for invoice in record.invoice_ids:
                if invoice.payment_state == "paid":
                    paid = True
                elif invoice.payment_state == "partial":
                    partial = True
                else:
                    not_paid = True

            if partial or (paid and not_paid):
                record.account_status = "partial"
            elif not (paid or partial):
                record.account_status = "not_paid"
            else:
                record.account_status = "paid"

    @api.depends("picking_ids", "picking_ids.state")
    def _compute_shipping_status(self):
        for record in self:
            shipped = False
            not_shipped = False

            for delivery in record.picking_ids:
                if delivery.state == "done":
                    shipped = True
                else:
                    not_shipped = True

            if shipped and not_shipped:
                record.shipping_status = "partial"
            elif shipped:
                record.shipping_status = "shipped"
            else:
                record.shipping_status = "not_shipped"

    @api.depends("invoice_ids", "invoice_ids.amount_residual")
    def _compute_debt_amount(self):
        for record in self:
            record.debt_amount = sum(record.invoice_ids.mapped("amount_residual"))

    @api.depends("so_partner_payment_ids.account_payment_amount_signed")
    def _compute_total_payments_sum(self):
        for rec in self:
            rec.total_payments_sum = sum(line.account_payment_amount_signed for line in rec.so_partner_payment_ids)

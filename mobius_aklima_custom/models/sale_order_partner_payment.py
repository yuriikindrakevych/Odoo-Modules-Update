from odoo import api, fields, models


class SaleOrderPartnerPayment(models.Model):
    _name = "sale.order.partner.payment"
    _description = "Sale Order Partner's Payments"

    sale_order_id = fields.Many2one(comodel_name="sale.order", readonly=True)
    account_payment_id = fields.Many2one(
        comodel_name="account.payment",
        domain="[('partner_id', '=', partner_id)]",
        string="Partner Payment"
    )
    partner_id = fields.Many2one(related="sale_order_id.partner_id", store=True)
    account_payment_id_company_currency_id = fields.Many2one(related="account_payment_id.company_currency_id")
    account_payment_id_currency_id = fields.Many2one(related="account_payment_id.currency_id")
    account_payment_date = fields.Date(related="account_payment_id.date")
    account_payment_state = fields.Selection(related="account_payment_id.state")
    account_payment_amount_company_currency_signed = fields.Monetary(
        related="account_payment_id.amount_company_currency_signed",
        currency_field="account_payment_id_company_currency_id"
    )
    account_payment_amount_signed = fields.Monetary(
        related="account_payment_id.amount_signed",
        currency_field="account_payment_id_currency_id"
    )

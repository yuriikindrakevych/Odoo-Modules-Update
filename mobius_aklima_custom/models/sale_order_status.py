from odoo import api, fields, models


class SaleOrderStatus(models.Model):
    _name = "sale.order.status"
    _description = "Sale Order Status Tags"

    name = fields.Char(string="Status Name", required=True, translate=True)
    color = fields.Integer(string="Color Index", default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [("name_uniq", "unique (name)", "Status name already exists!"),]

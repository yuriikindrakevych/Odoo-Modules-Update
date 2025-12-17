from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        return True

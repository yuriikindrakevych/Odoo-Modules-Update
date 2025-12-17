from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Lead(models.Model):
    _inherit = "crm.lead"

    partner_id = fields.Many2one(required=True)
    priority = fields.Selection(required=True)

    @api.constrains("email_from", "phone")
    def _check_required_fields(self):
        for record in self:
            if not record.email_from and not record.phone:
                raise ValidationError("Either email or phone has to be specified.")
            if record.priority == "0":
                raise ValidationError("Priority has to be specified.")

    def action_set_lost(self, **additional_values):
        res = super().action_set_lost(**additional_values)

        for order in self.order_ids:
            if order.account_status == "not_paid" and order.shipping_status == "not_shipped":
                order._action_cancel()
                order.cancel_reason_id = self.lost_reason

        return res

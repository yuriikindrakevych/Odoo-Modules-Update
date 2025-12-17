from odoo import api, fields, models
from ..tools import email_formatter


class Lead(models.Model):
    _name = "crm.lead"
    _inherit = ["mobius.phone.national.mixin", "crm.lead"]

    email_formatted = fields.Char(compute="_compute_email_formatted", store=True, readonly=True)

    @api.depends("email_from")
    def _compute_email_formatted(self):
        for record in self:
            record.email_formatted = email_formatter.get_formatted_email(record.email_from)

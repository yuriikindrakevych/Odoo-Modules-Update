from odoo import fields, models, api


class MailMessage(models.Model):
    _inherit = "mail.message"

    customer_id = fields.Many2one("res.partner", string="Customer", compute="_compute_customer_id", store=True)

    def _get_customer_id(self, record, model):
        if record == False or record is None:
            return False
        if model == "crm.lead":
            return record.partner_id.id

    @api.depends("model", "res_id")
    def _compute_customer_id(self):
        for rec in self:
            rec.customer_id = False
            if not rec.model or not rec.res_id:
                return
            record = rec.env[rec.model].browse(rec.res_id)
            rec.customer_id = rec._get_customer_id(record, rec.model)


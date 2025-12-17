from datetime import datetime
import pytz

from odoo import models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["mobius.phone.national.mixin", "res.partner"]

    def _create_activity_google_sheet(self):
        self.ensure_one()
        activity_type = self.env.ref("mail.mail_activity_data_call", raise_if_not_found=False)
        if not activity_type:
            return

        self.env["mail.activity"].with_context(mail_activity_quick_update=True).sudo().create({
            "res_name": self.name or "Contact",
            "activity_type_id": activity_type.id,
            "summary": self.name or "New Contact",
            "res_model_id": self.env["ir.model"]._get_id("res.partner"),
            "res_id": self.id,
            "date_deadline": datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"),
            "user_id": self.user_id.id or self.env.uid,
            "automated": True,
        })

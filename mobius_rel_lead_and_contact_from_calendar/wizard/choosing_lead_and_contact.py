from odoo import fields, models, api


class ChoosingLeadAndContactWizard(models.TransientModel):
    _name = "choosing.lead.and.contact.wizard"
    _description = "Choosing Lead And Contact Wizard"

    calendar_event_id = fields.Many2one(comodel_name="calendar.event")

    opportunity_old_id = fields.Many2one(comodel_name="crm.lead")
    contact_old_id = fields.Many2one(comodel_name="res.partner")
    opportunity_id = fields.Many2one(comodel_name="crm.lead")
    contact_id = fields.Many2one(comodel_name="res.partner")

    created_meet_from_calendar_res_id = fields.Integer()
    created_meet_from_calendar_res_model_id = fields.Many2one(
        comodel_name="ir.model")

    @api.model
    def default_get(self, vals):
        res = super().default_get(vals)
        res["calendar_event_id"] = \
            self.env.context.get("default_wizard_calendar_event_id")
        res["opportunity_old_id"] = \
            self.env.context.get("default_wizard_opportunity_id")
        res["opportunity_id"] = \
            self.env.context.get("default_wizard_opportunity_id")
        res["contact_old_id"] = \
            self.env.context.get("default_wizard_contact_id")
        res["contact_id"] = \
            self.env.context.get("default_wizard_contact_id")
        res["created_meet_from_calendar_res_id"] = self.env.context.get(
            "default_wizard_created_meet_from_calendar_res_id")
        res["created_meet_from_calendar_res_model_id"] = self.env.context.get(
            "default_wizard_created_meet_from_calendar_res_model_id")
        return res

    def confirm_changes(self):
        if (self.opportunity_id != self.opportunity_old_id or
                self.contact_id != self.contact_old_id):

            self._unlink_old_created_meet()
            crm_lead = self._get_crm_lead()
            res_partner = self._get_res_partner()
            mail_type = self._get_mail_type()

            if (self.opportunity_id and
                    self.opportunity_id != self.opportunity_old_id):
                created_meet_id = self.env["mail.activity"].sudo().create({
                    "res_model_id": crm_lead.id,
                    "res_id": self.opportunity_id.id,
                    "activity_type_id": mail_type.id,
                    "summary": self.opportunity_id.name,
                    "user_id": self.env.user.id
                })
                self.calendar_event_id.sudo().write({
                    "opportunity_id": self.opportunity_id.id,
                    "res_id": self.opportunity_id.id,
                    "res_model_id": crm_lead.id,
                    "created_meet_from_calendar_res_id": created_meet_id.id,
                    "created_meet_from_calendar_res_model_id": crm_lead.id,
                    "contact_id": False
                })
            elif self.contact_id and self.contact_id != self.contact_old_id:
                created_meet_id = self.env["mail.activity"].sudo().create({
                    "res_model_id": res_partner.id,
                    "res_id": self.contact_id.id,
                    "activity_type_id": mail_type.id,
                    "summary": self.contact_id.name,
                    "user_id": self.env.user.id
                })
                self.calendar_event_id.sudo().write({
                    "contact_id": self.contact_id.id,
                    "res_id": self.contact_id.id,
                    "res_model_id": res_partner.id,
                    "partner_ids": [(4, self.contact_id.id)],
                    "created_meet_from_calendar_res_id": created_meet_id.id,
                    "created_meet_from_calendar_res_model_id": res_partner.id,
                    "opportunity_id": False
                })
            else:
                self.calendar_event_id.sudo().write({
                    "opportunity_id": False,
                    "contact_id": False,
                    "res_id": 0,
                    "res_model_id": False,
                    "created_meet_from_calendar_res_id": 0,
                    "created_meet_from_calendar_res_model_id": False
                })

    def _unlink_old_created_meet(self):
        if (self.created_meet_from_calendar_res_id and
                self.created_meet_from_calendar_res_model_id):

            mail_activity = self.env["mail.activity"].sudo().search([
                ("id", "=", self.created_meet_from_calendar_res_id),
                ("res_model_id", "=",
                 self.created_meet_from_calendar_res_model_id.id)
            ])
            mail_activity.sudo().unlink()
        return True

    def _get_crm_lead(self):
        crm_lead = self.env["ir.model"].sudo().search([
            ("model", "=", "crm.lead")], limit=1)
        return crm_lead

    def _get_res_partner(self):
        res_partner = self.env["ir.model"].sudo().search([
            ("model", "=", "res.partner")], limit=1)
        return res_partner

    def _get_mail_type(self):
        mail_type = self.env["mail.activity.type"].sudo().search([
            ("category", "=", "meeting")], limit=1)
        return mail_type

from odoo import models, fields, api, _


class Meeting(models.Model):
    _inherit = "calendar.event"

    contact_id = fields.Many2one(comodel_name="res.partner")
    created_meet_from_calendar_res_id = fields.Integer()
    created_meet_from_calendar_res_model_id = fields.Many2one(
        comodel_name="ir.model")
    assigned_to = fields.Char(compute='_compute_assigned_to', readonly=True)

    @api.depends("res_id", "res_model_id")
    def _compute_assigned_to(self):
        for obj in self:
            if (obj.res_id and obj.res_model_id and
                    obj.sudo().res_model_id.model in ("crm.lead", "res.partner")):
                assigned_to = self.env[obj.res_model_id.model].search([
                    ("id", "=", obj.res_id)], limit=1)
                obj.assigned_to = _("ASSIGNED TO {}").format(assigned_to.name)
            else:
                obj.assigned_to = _("NOT ASSIGNED")

    def action_choosing_lead_and_contact(self):
        for obj in self:
            if obj.id:
                action = self.env.ref(
                    "mobius_rel_lead_and_contact_from_calendar.mobius_rel_"
                    "lead_and_contact_from_calendar_choosing_lead_and_contact_"
                    "wizard_action_window").sudo().read()[0]
                action["context"] = {
                    "default_wizard_calendar_event_id": obj.id,
                    "default_wizard_opportunity_id": obj.opportunity_id.id,
                    "default_wizard_contact_id": obj.contact_id.id,
                    "default_wizard_created_meet_from_calendar_res_id":
                        obj.created_meet_from_calendar_res_id,
                    "default_wizard_created_meet_from_calendar_res_model_id":
                        obj.created_meet_from_calendar_res_model_id.id
                }
                return action
            return super().action_choosing_lead_and_contact()

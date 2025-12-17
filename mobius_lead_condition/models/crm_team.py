from odoo import models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    def action_open_lead_with_condition(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "mobius_lead_condition.mobius_lead_condition_crm_lead_action_"
            "group_by_condition")

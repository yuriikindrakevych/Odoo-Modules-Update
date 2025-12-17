from odoo import models, fields, api


class Lead(models.Model):
    _inherit = "crm.lead"

    lead_condition_id = fields.Many2one(
        comodel_name="crm.lead.condition",
        group_expand="_read_group_lead_condition",
        domain=lambda self: "[('crm_team_id', '=', team_id)]", )

    @api.model
    def _read_group_lead_condition(self, stages, domain, order):
        # if team_id set in domain
        if domain:
            for el in domain:
                if el[0] == "team_id":
                    if el[1] not in ["=", '=']:
                        continue
                    lead_condition_ids = \
                        self.env["crm.lead.condition"].search([
                            ("crm_team_id", "=", el[2])])
                    return lead_condition_ids
        # else - by sale team of current user
        crm_team = self.env["crm.team"].search([
            ("member_ids", "in", [self.env.user.id])], limit=1)
        domain = []
        if crm_team:
            domain.append(("crm_team_id", "=", crm_team.id))
        lead_condition_ids = self.env["crm.lead.condition"].search(domain)
        return lead_condition_ids

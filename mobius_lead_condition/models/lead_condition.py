from odoo import models, fields


class LeadCondition(models.Model):
    _name = "crm.lead.condition"
    _description = 'CRM Lead Condition'

    name = fields.Char()
    crm_team_id = fields.Many2one(
        comodel_name="crm.team", string="Sales Team", )

# -*- coding: utf-8 -*-
from odoo import api, models


class Lead(models.Model):
    _inherit = "crm.lead"

    @api.depends('user_id', 'type', 'partner_id.team_id')
    def _compute_team_id(self):
        super()._compute_team_id()

        for record in self:
            company = record.company_id or self.env.company

            autofill_team_ids = company.contact_autofill_team_ids.ids

            if record.partner_id and record.partner_id.team_id and record.partner_id.team_id.id in autofill_team_ids:
                record.team_id = record.partner_id.team_id.id

# -*- coding: utf-8 -*-
from odoo import api, models


class Lead(models.Model):
    _inherit = "crm.lead"

    @api.depends('user_id', 'type', 'partner_id')
    def _compute_team_id(self):
        super()._compute_team_id()

        for record in self:
            company = record.company_id or self.env.company

            autofill_team_ids = company.contact_autofill_team_ids.ids

            partner_team_id = getattr(record.partner_id, 'team_id', False)
            if record.partner_id and partner_team_id and partner_team_id.id in autofill_team_ids:
                record.team_id = partner_team_id.id

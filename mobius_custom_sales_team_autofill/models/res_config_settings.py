# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contact_autofill_team_ids = fields.Many2many(comodel_name="crm.team",
                                                 string="Sales Team",
                                                 related="company_id.contact_autofill_team_ids",
                                                 readonly=False)

    def write(self, vals):
        res = super().write(vals)

        if "contact_autofill_team_ids" in vals:
            self.env.company.write({"contact_autofill_team_ids": vals.get("contact_autofill_team_ids")})

        return res

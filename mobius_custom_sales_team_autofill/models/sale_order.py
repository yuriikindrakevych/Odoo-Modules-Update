# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_default_team_new(self):
        autofill_team_ids = self.env.company.contact_autofill_team_ids.ids
        partner_team_id = getattr(self.partner_id, 'team_id', False)

        if partner_team_id and partner_team_id.id in autofill_team_ids:
            return partner_team_id

        return super()._get_default_team()

    team_id = fields.Many2one(default=_get_default_team_new)

    def _update_team_id_from_partner(self):
        autofill_team_ids = self.env.company.contact_autofill_team_ids.ids
        partner_team_id = getattr(self.partner_id, 'team_id', False)
        if partner_team_id and partner_team_id.id in autofill_team_ids:
            self.team_id = partner_team_id

    @api.onchange('user_id')
    def onchange_user_id(self):
        super().onchange_user_id()
        self._update_team_id_from_partner()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        self._update_team_id_from_partner()

# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_team_id(self):
        """Override to use partner's team_id if it's in the autofill list."""
        cached_teams = {}
        for order in self:
            # Check if partner has a team in the autofill list
            autofill_team_ids = order.company_id.contact_autofill_team_ids.ids
            partner_team = order.partner_id.team_id if order.partner_id else False

            if partner_team and partner_team.id in autofill_team_ids:
                order.team_id = partner_team
            else:
                # Fall back to standard Odoo 18 logic
                default_team_id = self.env.context.get('default_team_id', False) or order.team_id.id
                user_id = order.user_id.id
                company_id = order.company_id.id
                key = (default_team_id, user_id, company_id)
                if key not in cached_teams:
                    cached_teams[key] = self.env['crm.team'].with_context(
                        default_team_id=default_team_id,
                    )._get_default_team_id(
                        user_id=user_id,
                        domain=self.env['crm.team']._check_company_domain(company_id),
                    )
                order.team_id = cached_teams[key]

    def _update_team_id_from_partner(self):
        autofill_team_ids = self.env.company.contact_autofill_team_ids.ids
        partner_team_id = self.partner_id.team_id if self.partner_id else False
        if partner_team_id and partner_team_id.id in autofill_team_ids:
            self.team_id = partner_team_id

    @api.onchange('user_id')
    def onchange_user_id(self):
        # Odoo 18: onchange_user_id removed from base, call only if exists
        if hasattr(super(), 'onchange_user_id'):
            super().onchange_user_id()
        self._update_team_id_from_partner()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        # Odoo 18: onchange_partner_id removed from base, call only if exists
        if hasattr(super(), 'onchange_partner_id'):
            super().onchange_partner_id()
        self._update_team_id_from_partner()

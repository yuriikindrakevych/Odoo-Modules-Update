#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _


class ResPartner(models.Model):
    _inherit = "res.partner"

    agent = fields.Many2one("res.partner", string="Agent")

    @api.onchange("city_ua")
    def _onchange_city(self):
        if self.city_ua and not self.state_id:
            city = self.env["mobius_catalogue_koatuu.settlement"].search([("id", "=", self.city_ua.id)], limit=1)
            if city:
                self.state_id = city.res_country_state_id
            else:
                self.state_id = None
                raise ValidationError(_("First choose the state!"))
        else:
            self.city = self.city_ua.name

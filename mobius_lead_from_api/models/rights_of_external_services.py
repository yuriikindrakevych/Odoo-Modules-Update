#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api

class RightsOfExternalServices(models.Model):
    _name = "rights.of.external.services"

    name = fields.Char("Code")
    description = fields.Char("Description", translate=True)
    partner_id = fields.Many2one("res.partner", "Partner")

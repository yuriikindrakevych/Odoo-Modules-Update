# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    global_location_number = fields.Char(
        string="Global Location Number",
        help="GLN (Global Location Number) - 13-digit GS1 identifier for locations and parties",
    )

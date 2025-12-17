#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    description = fields.Char(translate=True)

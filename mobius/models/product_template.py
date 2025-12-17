#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _name    = "product.template"
    _inherit = ["product.template", "barcode.generate.mixin.mobius"]

    category_desc = fields.Char(related="categ_id.category_desc")
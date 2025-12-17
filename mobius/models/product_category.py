#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductCategory(models.Model):
    _inherit = "product.category"

    category_desc = fields.Char("Category Description", translate=True)
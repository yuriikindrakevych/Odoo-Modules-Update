#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = "product.category"

    product_attribute_ids = fields.Many2many(comodel_name="product.attribute", string="Product Attribute")
#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    delete_me = fields.Boolean(help="Technical field", default=False)
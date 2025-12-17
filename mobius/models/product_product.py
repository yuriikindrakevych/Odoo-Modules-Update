#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "barcode.generate.mixin.mobius"]
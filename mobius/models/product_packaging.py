#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import models


class ProductPackaging(models.Model):
    _name = "product.packaging"
    _inherit = ["product.packaging", "barcode.generate.mixin.mobius"]

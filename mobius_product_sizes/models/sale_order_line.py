#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    serial_number = fields.Char("Serial Number", help="Serial Number", index=True)

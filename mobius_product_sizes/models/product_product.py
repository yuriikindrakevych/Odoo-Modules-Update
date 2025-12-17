#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductProduct(models.Model):
    _name    = "product.product"
    _inherit = ["product.product"]
    _inherits = {"product.template": "product_tmpl_id"}

    volume = fields.Float(compute="_compute_volume", readonly=True)

    @api.depends("length", "width", "height", "length_uom_id", "volume_uom_id")
    def _compute_volume(self):
        for product in self:
            product.volume = product._calculate_volume(
                product.length,
                product.width,
                product.height,
                product.length_uom_id,
                product.volume_uom_id,
            )

    def _calculate_volume(self, length, width, height, length_uom_id, volume_uom_id):
        volume_m3 = 0
        if length and width and height and length:
            length_m = self.convert_to_meters(length, length_uom_id)
            width_m = self.convert_to_meters(width, length_uom_id)
            height_m = self.convert_to_meters(height, length_uom_id)
            volume_m3 = length_m * height_m * width_m
        volume_in_volume_uom = self.convert_to_volume_uom(volume_m3, volume_uom_id)
        return volume_in_volume_uom

    def convert_to_meters(self, measure, length_uom_id):
        uom_meters = self.env.ref("uom.product_uom_meter")
        return length_uom_id._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False,
        )

    def convert_to_volume_uom(self, measure, volume_uom_id):
        uom_m3 = self.env.ref("uom.product_uom_cubic_meter")
        return uom_m3._compute_quantity(
            qty=measure,
            to_unit=volume_uom_id,
            round=False,
        )

class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category"]

    name = fields.Char("Name", index=True, required=True, translate=True)
#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _name    = "product.template"
    _inherit = ["product.template"]

    def _get_length_uom_id_for_mm(self):
        id_mm = self.env.ref("uom.product_uom_millimeter").id
        return id_mm

    volume = fields.Float(compute="_compute_volume", readonly=True)
    volume_uom_id = fields.Many2one(
        "uom.uom",
        string="Volume Units of Measure",
        domain=lambda self: [("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id)],
        help="Packaging volume unit of measure",
        default=lambda self: self.env["product.template"]._get_volume_uom_id_from_ir_config_parameter(),
        readonly=True
    )


    length = fields.Integer("Length", store=True)
    length_uom_id = fields.Many2one(
        "uom.uom",
        string="Length Unit of Measure",
        domain=lambda self: [("category_id", "=", self.env.ref("uom.uom_categ_length").id)],
        default=_get_length_uom_id_for_mm,
        readonly=True,
    )
    length_uom_name = fields.Char(string="Length Unit of Measure label", related="length_uom_id.name", readonly=True)


    width = fields.Integer("Width", store=True)
    width_uom_id = fields.Many2one(
        "uom.uom",
        string="Width Unit of Measure",
        domain=lambda self: [("category_id", "=", self.env.ref("uom.uom_categ_length").id)],
        default=_get_length_uom_id_for_mm,
        readonly=True,
    )
    width_uom_name = fields.Char(string="Width Unit of Measure label", related="width_uom_id.name", readonly=True)


    height = fields.Integer("Height", store=True)
    height_uom_id = fields.Many2one(
        "uom.uom",
        string="Height Unit of Measure",
        domain=lambda self: [("category_id", "=", self.env.ref("uom.uom_categ_length").id)],
        default=_get_length_uom_id_for_mm,
        readonly=True,
    )
    height_uom_name = fields.Char(string="Height Unit of Measure label", related="height_uom_id.name", readonly=True)


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
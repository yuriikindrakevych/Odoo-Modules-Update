#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


import inspect
import traceback

class BuildingObjectLine(models.Model):
    _name = "building.object.line"
    _order = "sequence,id"

    building_object_id = fields.Many2one("building.object", "Building Object", required=True)

    order_line_building_line = fields.One2many('sale.order.line', 'order_building_line_id', string='Order Lines', copy=True, auto_join=True)

    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True)",
        change_default=True, ondelete='restrict', check_company=True)
    price_unit = fields.Float('Unit Price', digits='Product Price')
    demand = fields.Integer("Demand")
    order = fields.Integer("Sale")
    reserved = fields.Integer("Reserved", compute="_compute_reserved", readonly=True, store=True)
    check_box = fields.Boolean()  #deleTe me
    full_reserved = fields.Boolean(compute="_compute_full_reserved")

    def _get_price_unit(self, product_id):
        domain = ['|',
            '&', ('product_tmpl_id', '=', product_id.product_tmpl_id.id), ('applied_on', '=', '1_product'),
            '&', ('product_id', '=', product_id.id), ('applied_on', '=', '0_product_variant')]
        product_pricelist_item = self.env["product.pricelist.item"].search(domain, limit=1)
        if product_pricelist_item:
            return float(product_pricelist_item[0].fixed_price)
        else:
            return 1.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            price_unit = self._get_price_unit(self.product_id)
            self.price_unit = price_unit

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('product_id'):
    #             product_id = self.env["product.product"].browse(vals.get('product_id'))
    #             if product_id:
    #                 price_unit = self._get_price_unit(product_id)
    #                 #price_unit = 1.0
    #                 vals["price_unit"] = price_unit
    #     return super().create(vals_list)

    @api.constrains('order')
    def _check_order(self):
        if self.order < 0:
            raise ValidationError(_('The quantity for sale cannot be less than zero'))
        if self.order + self.reserved > self.demand:
            raise ValidationError(_('You cannot sell more than demand.'))

    @api.depends("reserved")
    def _compute_full_reserved(self):
        for rec in self:
            if rec.reserved is rec.demand:
                rec.full_reserved = True
            else:
                rec.full_reserved = False


    @api.depends("order_line_building_line.product_uom_qty", "order_line_building_line", "order_line_building_line.order_id.state")
    def _compute_reserved(self):
        for rec in self:
            sum = 0
            for sale_line in rec.order_line_building_line:
                if sale_line.order_id.state == "cancel":
                    continue
                sum += sale_line.product_uom_qty
            rec.reserved = sum
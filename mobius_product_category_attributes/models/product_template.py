#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def create_attribute(self):
        if self.categ_id and self.categ_id.product_attribute_ids:
            for attribute in self.categ_id.product_attribute_ids:
                delete_me = attribute.value_ids.filtered(lambda x: x.delete_me == True)
                if not delete_me:
                    next_number = self.env["ir.sequence"].next_by_code("attribute_delete_me")
                    delete_me = self.env["product.attribute.value"].create({
                        "delete_me": True,
                        "name": "delete_me {}".format(next_number),
                        "attribute_id": attribute.id,
                    })
                self.env["product.template.attribute.line"].create({
                        "product_tmpl_id": self._origin.id,
                        "attribute_id": attribute.id,
                        "value_ids": [(4, delete_me.id)],
                })